"""
AFOLIE Input批次图像节点（V3 API）
从指定文件夹加载批次图像，保留PNG透明通道（RGBA）
"""

import os
import torch
import numpy as np
from PIL import Image
import folder_paths

from comfy_api.latest import io
from ..utils import pil2tensor


FILE_FORMATS = ["all", "png", "jpg"]

INPUT_RESAMPLING_METHODS = [
    "保留细节(Lanczos)",
    "两次立方(Bicubic)",
    "两次线性(Bilinear)",
    "邻近(Nearest)"
]

INPUT_RESAMPLE_MAP = {
    "保留细节(Lanczos)": Image.LANCZOS,
    "两次立方(Bicubic)": Image.BICUBIC,
    "两次线性(Bilinear)": Image.BILINEAR,
    "邻近(Nearest)": Image.NEAREST
}


def _get_valid_extensions(文件格式):
    if 文件格式 == "png":
        return ['.png']
    elif 文件格式 == "jpg":
        return ['.jpg', '.jpeg']
    else:
        return ['.png', '.jpg', '.jpeg']


def _get_image_files(folder_path, 文件格式):
    valid_extensions = _get_valid_extensions(文件格式)
    image_files = []
    try:
        for filename in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in valid_extensions:
                    image_files.append(file_path)
    except Exception as e:
        print(f"读取文件夹失败: {folder_path}, 错误: {str(e)}")
    return image_files


def _process_pil_image(pil_img, ext):
    """根据文件格式处理 PIL 图像，保留PNG透明通道"""
    if ext == '.png':
        # PNG保留原始模式（RGBA或RGB）
        if pil_img.mode == 'RGBA':
            pass  # 保留alpha
        elif pil_img.mode == 'P' and 'transparency' in pil_img.info:
            pil_img = pil_img.convert('RGBA')
        else:
            pil_img = pil_img.convert('RGB')
    elif ext in ['.jpg', '.jpeg']:
        # JPG不支持透明，保持RGB
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
    else:
        if pil_img.mode == 'RGBA':
            pass
        else:
            pil_img = pil_img.convert('RGB')
    return pil_img


def _resize_pil_with_alpha(pil_img, target_size, rgb_filter):
    """缩放PIL图像，分别处理RGB和Alpha通道"""
    if pil_img.mode == 'RGBA':
        r, g, b, a = pil_img.split()
        rgb = Image.merge('RGB', (r, g, b))
        rgb_resized = rgb.resize(target_size, rgb_filter)
        a_resized = a.resize(target_size, Image.NEAREST)
        rgb_resized.putalpha(a_resized)
        return rgb_resized
    else:
        return pil_img.resize(target_size, rgb_filter)


def _empty_image():
    return torch.zeros((1, 64, 64, 3))


class AFOLIEInputBatchImages(io.ComfyNode):
    """Input批次图像节点 - 从指定文件夹加载图像（保持原始尺寸），PNG保留透明通道"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIEInput批次图像",
            display_name="Input批次图像 📁",
            category="AFOLIE/input",
            description="从指定文件夹加载批次图像（保持原始尺寸），PNG保留透明通道(RGBA)",
            inputs=[
                io.String.Input("路径", default="E:/AI/ComfyUI_works/input_images", multiline=False),
                io.Combo.Input("文件格式", options=FILE_FORMATS),
            ],
            outputs=[
                io.Image.Output("图像", is_output_list=True),
            ],
        )

    @classmethod
    def execute(cls, 路径, 文件格式="all"):
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            return io.NodeOutput([_empty_image()])

        image_files = _get_image_files(folder_path, 文件格式)
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            return io.NodeOutput([_empty_image()])

        loaded_images = []
        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                _, ext = os.path.splitext(img_path.lower())
                pil_img = _process_pil_image(pil_img, ext)
                img_tensor = pil2tensor(pil_img)
                loaded_images.append(img_tensor)
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue

        if not loaded_images:
            print("没有成功加载任何图像")
            return io.NodeOutput([_empty_image()])

        print(f"成功加载 {len(loaded_images)} 张图像，将逐张输出")
        return io.NodeOutput(loaded_images)


class AFOLIEInputBatchImagePixels(io.ComfyNode):
    """Input批次图像像素节点 - 加载图像并统一调整到指定像素尺寸，PNG保留透明通道"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIEInput批次图像像素",
            display_name="Input批次图像像素 📐",
            category="AFOLIE/input",
            description="从指定文件夹加载批次图像，并统一调整到指定像素尺寸，PNG保留透明通道(RGBA)",
            inputs=[
                io.String.Input("路径", default="E:/AI/ComfyUI_works/input_images", multiline=False),
                io.Combo.Input("文件格式", options=FILE_FORMATS),
                io.Int.Input("统一宽度", default=512, min=64, max=8192, step=64),
                io.Int.Input("统一高度", default=512, min=64, max=8192, step=64),
                io.Combo.Input("采样方法", options=INPUT_RESAMPLING_METHODS),
            ],
            outputs=[
                io.Image.Output("图像", is_output_list=True),
            ],
        )

    @classmethod
    def execute(cls, 路径, 文件格式="all", 统一宽度=512, 统一高度=512, 采样方法="保留细节(Lanczos)"):
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            return io.NodeOutput([_empty_image()])

        image_files = _get_image_files(folder_path, 文件格式)
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            return io.NodeOutput([_empty_image()])

        resample_filter = INPUT_RESAMPLE_MAP.get(采样方法, Image.LANCZOS)
        target_size = (统一宽度, 统一高度)
        loaded_images = []
        resized_count = 0

        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                original_size = pil_img.size
                _, ext = os.path.splitext(img_path.lower())
                pil_img = _process_pil_image(pil_img, ext)

                pil_img = _resize_pil_with_alpha(pil_img, target_size, resample_filter)
                if original_size != target_size:
                    resized_count += 1
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)} ({original_size[0]}x{original_size[1]} -> {target_size[0]}x{target_size[1]})")

                loaded_images.append(pil2tensor(pil_img))
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue

        if not loaded_images:
            print("没有成功加载任何图像")
            return io.NodeOutput([_empty_image()])

        print(f"成功加载 {len(loaded_images)} 张图像 (其中 {resized_count} 张已调整尺寸到 {target_size[0]}x{target_size[1]})，将逐张输出")
        return io.NodeOutput(loaded_images)


class AFOLIEInputBatchImageScale(io.ComfyNode):
    """Input批次图像倍数节点 - 加载图像并按倍数统一缩放，PNG保留透明通道"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIEInput批次图像倍数",
            display_name="Input批次图像倍数 🔢",
            category="AFOLIE/input",
            description="从指定文件夹加载批次图像，并按倍数统一缩放，PNG保留透明通道(RGBA)",
            inputs=[
                io.String.Input("路径", default="E:/AI/ComfyUI_works/input_images", multiline=False),
                io.Combo.Input("文件格式", options=FILE_FORMATS),
                io.Float.Input("倍数", default=1.0, min=0.01, max=12.0, step=0.01),
                io.Combo.Input("采样方法", options=INPUT_RESAMPLING_METHODS),
            ],
            outputs=[
                io.Image.Output("图像", is_output_list=True),
            ],
        )

    @classmethod
    def execute(cls, 路径, 文件格式="all", 倍数=1.0, 采样方法="保留细节(Lanczos)"):
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            return io.NodeOutput([_empty_image()])

        image_files = _get_image_files(folder_path, 文件格式)
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            return io.NodeOutput([_empty_image()])

        resample_filter = INPUT_RESAMPLE_MAP.get(采样方法, Image.LANCZOS)

        # 用第一张图像的尺寸作为基准
        first_img = Image.open(image_files[0])
        base_width, base_height = first_img.size
        target_width = max(1, int(base_width * 倍数))
        target_height = max(1, int(base_height * 倍数))
        target_size = (target_width, target_height)

        print(f"基准尺寸: {base_width}x{base_height}, 倍数: {倍数}, 目标尺寸: {target_width}x{target_height}")

        loaded_images = []

        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                original_size = pil_img.size
                _, ext = os.path.splitext(img_path.lower())
                pil_img = _process_pil_image(pil_img, ext)

                pil_img = _resize_pil_with_alpha(pil_img, target_size, resample_filter)
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)} ({original_size[0]}x{original_size[1]} -> {target_size[0]}x{target_size[1]})")

                loaded_images.append(pil2tensor(pil_img))
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue

        if not loaded_images:
            print("没有成功加载任何图像")
            return io.NodeOutput([_empty_image()])

        print(f"成功加载 {len(loaded_images)} 张图像 (全部缩放到 {target_size[0]}x{target_size[1]})，将逐张输出")
        return io.NodeOutput(loaded_images)
