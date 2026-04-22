"""
AFOLIE Image Size Nodes - 图像缩放节点（V3 API）
提供像素和倍数两种缩放方式，以及像素对齐功能
所有节点默认支持RGBA图像（alpha通道内置），遮罩作为备选输入
"""

import os
import subprocess
import tempfile
import torch
import numpy as np
from PIL import Image, ImageDraw

from comfy_api.latest import io
from .utils import tensor2pil, pil2tensor, resize_image_with_alpha


# 采样方法列表（两个节点共用）
SAMPLING_METHODS = [
    "两次立方(平滑渐变)",
    "保留细节(扩大)",
    "保留细节2.0",
    "两次立方(较平滑)(扩大)",
    "两次立方(较锐利)(缩减)",
    "邻近(硬边缘)",
    "两次线性"
]


# 采样方法到 PIL 滤镜的映射
RESAMPLE_MAP = {
    "两次立方(平滑渐变)": Image.BICUBIC,
    "保留细节(扩大)": Image.LANCZOS,
    "保留细节2.0": Image.LANCZOS,
    "两次立方(较平滑)(扩大)": Image.BICUBIC,
    "两次立方(较锐利)(缩减)": Image.BICUBIC,
    "邻近(硬边缘)": Image.NEAREST,
    "两次线性": Image.BILINEAR
}


class AFOLIEImagePixelResize(io.ComfyNode):
    """图像像素缩放节点 - 支持RGBA图像，alpha通道随图像一起缩放"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE图像像素缩放",
            display_name="图像像素缩放 📐",
            category="AFOLIE/图像",
            description="通过指定宽度和高度来调整图像大小，RGBA图像alpha通道自动随图像缩放",
            inputs=[
                io.Image.Input("图像"),
                io.Int.Input("宽度", default=512, min=2, max=2048, step=1),
                io.Int.Input("高度", default=512, min=2, max=2048, step=1),
                io.Combo.Input("采样方法", options=SAMPLING_METHODS),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.Mask.Output("遮罩"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 宽度, 高度, 采样方法, mask=None):
        pil_filter = RESAMPLE_MAP.get(采样方法, Image.BICUBIC)
        result, mask_result = resize_image_with_alpha(
            图像, (宽度, 高度), pil_filter, mask=mask
        )
        return io.NodeOutput(result, mask_result)


class AFOLIEImageScaleResize(io.ComfyNode):
    """图像倍数缩放节点 - 支持RGBA图像，alpha通道随图像一起缩放"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE图像倍数缩放",
            display_name="图像倍数缩放 🔢",
            category="AFOLIE/图像",
            description="通过倍数来调整图像大小，RGBA图像alpha通道自动随图像缩放",
            inputs=[
                io.Image.Input("图像"),
                io.Float.Input("倍数", default=1.0, min=0.01, max=12.0, step=0.01),
                io.Combo.Input("采样方法", options=SAMPLING_METHODS),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.Mask.Output("遮罩"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 倍数, 采样方法, mask=None):
        _, orig_height, orig_width, _ = 图像.shape
        target_width = max(1, int(orig_width * 倍数))
        target_height = max(1, int(orig_height * 倍数))
        pil_filter = RESAMPLE_MAP.get(采样方法, Image.BICUBIC)

        result, mask_result = resize_image_with_alpha(
            图像, (target_width, target_height), pil_filter, mask=mask
        )
        return io.NodeOutput(result, mask_result)


class AFOLIEImageGridCrop(io.ComfyNode):
    """图像网格裁剪节点 - 支持RGBA图像，裁剪时保留alpha通道"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE图像网格裁剪",
            display_name="图像网格裁剪 ✂️",
            category="AFOLIE/图像",
            description="根据横向和纵向数量将图像均匀裁剪成多个子图像，保留alpha通道",
            inputs=[
                io.Image.Input("图像"),
                io.Int.Input("横向数量", default=2, min=0, max=20, step=1,
                             tooltip="水平方向分割数量，0表示不横向裁剪"),
                io.Int.Input("纵向数量", default=2, min=0, max=20, step=1,
                             tooltip="垂直方向分割数量，0表示不纵向裁剪"),
            ],
            outputs=[
                io.Image.Output("裁剪图像"),
                io.Image.Output("预览图像"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 横向数量, 纵向数量):
        batch_size, orig_height, orig_width, channels = 图像.shape

        actual_横向数量 = max(1, 横向数量)
        actual_纵向数量 = max(1, 纵向数量)

        block_width = (orig_width + actual_横向数量 - 1) // actual_横向数量
        block_height = (orig_height + actual_纵向数量 - 1) // actual_纵向数量

        all_cropped_images = []
        preview_images = []

        for b in range(batch_size):
            # tensor2pil 自动处理 RGBA(4通道)
            pil_img = tensor2pil(图像[b])
            preview_images.append(pil2tensor(pil_img))

            for row in range(actual_纵向数量):
                for col in range(actual_横向数量):
                    left = col * block_width
                    upper = row * block_height
                    right = min(left + block_width, orig_width)
                    lower = min(upper + block_height, orig_height)

                    cropped_pil = pil_img.crop((left, upper, right, lower))

                    actual_width = right - left
                    actual_height = lower - upper
                    if actual_width != block_width or actual_height != block_height:
                        # RGBA图像用NEAREST保持alpha边界清晰
                        cropped_pil = cropped_pil.resize(
                            (block_width, block_height), Image.NEAREST
                        )

                    all_cropped_images.append(pil2tensor(cropped_pil))

        cropped_result = torch.cat(all_cropped_images, dim=0)
        preview_result = torch.cat(preview_images, dim=0)

        return io.NodeOutput(cropped_result, preview_result)


class AFOLIEPixelAlign(io.ComfyNode):
    """像素对齐节点 - 支持RGBA图像，处理RGB后保留alpha通道"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE像素对齐",
            display_name="像素对齐 🎯",
            category="AFOLIE/图像",
            description="将像素对齐到完美网格，修复 AI 生成像素艺术的不一致，量化颜色到严格的调色板",
            inputs=[
                io.Image.Input("图像"),
                io.Int.Input("颜色数量", default=16, min=2, max=256, step=1,
                             tooltip="图像将被量化到这个数量的颜色"),
            ],
            outputs=[
                io.Image.Output("对齐后的图像"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 颜色数量):
        # 获取可执行文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(current_dir, "bin", "spritefusion-pixel-snapper.exe")

        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"找不到可执行文件: {exe_path}")

        try:
            batch_size = 图像.shape[0]
            channels = 图像.shape[3] if 图像.dim() == 4 else 3
            output_tensors = []

            for i in range(batch_size):
                single_image = 图像[i]
                original_height = single_image.shape[0]
                original_width = single_image.shape[1]

                # 提取alpha通道（如果有）
                alpha_pil = None
                if channels == 4:
                    alpha_np = (single_image[:, :, 3].cpu().numpy() * 255).astype(np.uint8)
                    alpha_pil = Image.fromarray(alpha_np, mode='L')
                    rgb_only = single_image[:, :, :3]
                else:
                    rgb_only = single_image

                # RGB部分转PIL处理
                np_image = (rgb_only.cpu().numpy() * 255).astype(np.uint8)
                pil_image = Image.fromarray(np_image, mode='RGB')

                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as input_file:
                    input_path = input_file.name
                    pil_image.save(input_path, 'PNG')

                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
                    output_path = output_file.name

                try:
                    cmd = [exe_path, input_path, output_path, str(颜色数量)]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else "未知错误"
                        raise RuntimeError(f"像素对齐处理失败: {error_msg}")

                    output_image = Image.open(output_path)

                    if output_image.mode != 'RGB':
                        output_image = output_image.convert('RGB')

                    if output_image.size != (original_width, original_height):
                        output_image = output_image.resize(
                            (original_width, original_height), Image.NEAREST
                        )

                    # 恢复alpha通道
                    if alpha_pil is not None:
                        if alpha_pil.size != output_image.size:
                            alpha_pil = alpha_pil.resize(output_image.size, Image.NEAREST)
                        output_image.putalpha(alpha_pil)

                    output_tensor = pil2tensor(output_image)
                    output_tensors.append(output_tensor)

                finally:
                    try:
                        os.unlink(input_path)
                    except:
                        pass
                    try:
                        os.unlink(output_path)
                    except:
                        pass

            result = torch.cat(output_tensors, dim=0)
            return io.NodeOutput(result)

        except Exception as e:
            raise RuntimeError(f"像素对齐节点错误: {str(e)}")
