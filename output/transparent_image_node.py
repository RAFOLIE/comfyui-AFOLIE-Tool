"""
AFOLIE 透明图像节点（V3 API）
预览和保存带透明通道的图像
自动检测RGBA图像(4通道)的alpha，同时支持MASK作为备选输入
"""

import os
import torch
import numpy as np
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import folder_paths

from comfy_api.latest import io
from ..utils import tensor2pil, generate_checkerboard, combine_to_rgba, mask_to_pil


def _get_alpha_source(图像, mask, 反转遮罩, batch_size):
    """统一处理alpha来源：图像4通道 > mask输入

    Args:
        图像: tensor [B,H,W,C]
        mask: optional tensor [B,H,W]
        反转遮罩: bool
        batch_size: int
    Returns:
        list[PIL.Image] - 每张图对应的alpha PIL图像(或None)
    """
    channels = 图像.shape[3] if 图像.dim() == 4 else 3
    alphas = []

    # 优先使用mask（备选输入）
    if mask is not None:
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        if mask.shape[0] == 1 and batch_size > 1:
            mask = mask.expand(batch_size, -1, -1)

        for i in range(batch_size):
            alphas.append(mask_to_pil(mask[i] if i < mask.shape[0] else mask[0], invert=反转遮罩))
        return alphas

    # 从4通道图像提取alpha
    if channels == 4:
        for i in range(batch_size):
            alpha_np = (图像[i, :, :, 3].cpu().numpy() * 255).astype(np.uint8)
            alphas.append(Image.fromarray(alpha_np, mode='L'))
        return alphas

    # 无alpha
    return [None] * batch_size


class AFOLIETransparentPreview(io.ComfyNode):
    """透明图像预览节点 - 自动检测RGBA图像alpha，支持MASK备选输入"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE透明图像预览",
            display_name="透明图像预览 👁️",
            category="AFOLIE/output",
            description="自动检测RGBA图像(4通道)的alpha并预览，也支持MASK作为备选遮罩输入",
            is_output_node=True,
            hidden=[io.Hidden.unique_id],
            inputs=[
                io.Image.Input("图像"),
                io.Boolean.Input("反转遮罩", default=True,
                    tooltip="开启后遮罩白色区域变为透明，黑色区域保留（适用于大多数抠图节点输出的遮罩）"),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.Mask.Output("遮罩"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 反转遮罩=True, mask=None, unique_id=None, extra_pnginfo=None):
        output_dir = folder_paths.get_temp_directory()
        batch_size = 图像.shape[0]
        channels = 图像.shape[3] if 图像.dim() == 4 else 3

        alphas = _get_alpha_source(图像, mask, 反转遮罩, batch_size)
        results = []

        for i in range(batch_size):
            # 只取RGB通道用于合成
            if channels == 4:
                pil_img = tensor2pil(图像[i, :, :, :3])
            else:
                pil_img = tensor2pil(图像[i])

            rgba_img = combine_to_rgba(pil_img, alphas[i])

            filename = f"afolie_preview_{unique_id}_{i:04d}.png"
            file_path = os.path.join(output_dir, filename)
            rgba_img.save(file_path, format='PNG', compress_level=1)

            results.append({
                "filename": filename,
                "subfolder": "",
                "type": "temp"
            })

        # 生成遮罩输出（备选）
        if any(a is not None for a in alphas):
            mask_result = torch.stack([
                torch.from_numpy(np.array(a).astype(np.float32) / 255.0) if a is not None
                else torch.ones(图像.shape[1], 图像.shape[2], dtype=torch.float32)
                for a in alphas
            ], dim=0)
        else:
            mask_result = torch.ones(
                batch_size, 图像.shape[1], 图像.shape[2],
                dtype=torch.float32
            )

        return io.NodeOutput(图像, mask_result, ui={"images": results})


class AFOLIETransparentSave(io.ComfyNode):
    """透明图像保存节点 - 自动检测RGBA图像alpha，支持MASK备选输入"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE透明图像保存",
            display_name="透明图像保存 💾",
            category="AFOLIE/output",
            description="自动检测RGBA图像(4通道)的alpha并保存为PNG，也支持MASK作为备选遮罩输入",
            is_output_node=True,
            hidden=[io.Hidden.unique_id],
            inputs=[
                io.Image.Input("图像"),
                io.Boolean.Input("反转遮罩", default=True,
                    tooltip="开启后遮罩白色区域变为透明，黑色区域保留（适用于大多数抠图节点输出的遮罩）"),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.Mask.Output("遮罩"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 反转遮罩=True, mask=None, unique_id=None, extra_pnginfo=None):
        output_dir = folder_paths.get_output_directory()
        batch_size = 图像.shape[0]
        img_height = 图像.shape[1]
        img_width = 图像.shape[2]
        channels = 图像.shape[3] if 图像.dim() == 4 else 3

        # 使用 ComfyUI 官方的文件路径生成方式
        filename_prefix = "ComfyUI"
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, output_dir, img_width, img_height
        )

        alphas = _get_alpha_source(图像, mask, 反转遮罩, batch_size)
        results = []

        # 准备元数据
        metadata = PngInfo()
        if extra_pnginfo is not None:
            for k, v in extra_pnginfo.items():
                metadata.add_text(k, str(v))
        metadata.add_text("Software", "ComfyUI - AFOLIE")

        for i in range(batch_size):
            # 只取RGB通道用于合成
            if channels == 4:
                pil_img = tensor2pil(图像[i, :, :, :3])
            else:
                pil_img = tensor2pil(图像[i])

            rgba_img = combine_to_rgba(pil_img, alphas[i])

            # ComfyUI 官方命名格式
            file = f"{filename}_{counter:05}_.png"
            file_path = os.path.join(full_output_folder, file)
            rgba_img.save(file_path, format='PNG', compress_level=4, pnginfo=metadata)

            print(f"透明图像已保存: {file_path}")
            counter += 1

            # 用透明 PNG 作为预览
            preview_filename = f"afolie_preview_{unique_id}_{i:04d}.png"
            preview_path = os.path.join(folder_paths.get_temp_directory(), preview_filename)
            rgba_img.save(preview_path, format='PNG', compress_level=1)

            results.append({
                "filename": preview_filename,
                "subfolder": "",
                "type": "temp"
            })

        # 生成遮罩输出（备选）
        if any(a is not None for a in alphas):
            mask_result = torch.stack([
                torch.from_numpy(np.array(a).astype(np.float32) / 255.0) if a is not None
                else torch.ones(img_height, img_width, dtype=torch.float32)
                for a in alphas
            ], dim=0)
        else:
            mask_result = torch.ones(
                batch_size, img_height, img_width,
                dtype=torch.float32
            )

        return io.NodeOutput(图像, mask_result, ui={"images": results})
