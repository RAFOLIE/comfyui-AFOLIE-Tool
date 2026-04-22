"""
AFOLIE 图片加载与浏览节点（V3 API）
加载图片：支持拖拽/粘贴上传，PNG透明通道保留在图像中(4通道RGBA)
浏览图片：纯预览查看节点，连接图像后直接在节点上预览（无输出端口）
"""

import os
from PIL import Image, ImageOps
import folder_paths

from comfy_api.latest import io
from ..utils import pil2tensor, tensor2pil


def _load_rgba_image(file_path):
    """加载图片，保留透明通道，返回RGBA张量

    Returns:
        tensor: [1,H,W,C] C=4(含透明) 或 C=3(不透明)
    """
    pil_img = Image.open(file_path)
    pil_img = ImageOps.exif_transpose(pil_img)

    # 统一转为 RGBA（保留透明通道）
    if pil_img.mode == 'RGBA':
        pass  # 已经是RGBA
    elif pil_img.mode == 'LA':
        l, a = pil_img.split()
        rgb = l.convert('RGB')
        pil_img = Image.merge('RGB', (rgb.split()[0], rgb.split()[1], rgb.split()[2]))
        pil_img.putalpha(a)
    elif pil_img.mode == 'P' and 'transparency' in pil_img.info:
        pil_img = pil_img.convert('RGBA')
    else:
        pil_img = pil_img.convert('RGB')

    return pil2tensor(pil_img)


def _get_input_image_files():
    """获取ComfyUI input目录中的图片文件列表"""
    input_dir = folder_paths.get_input_directory()
    files = [
        f for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]
    try:
        files = folder_paths.filter_files_content_types(files, ["image"])
    except AttributeError:
        valid_ext = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.tif')
        files = [f for f in files if f.lower().endswith(valid_ext)]
    return sorted(files)


class AFOLIELoadImage(io.ComfyNode):
    """加载图片节点 - 支持拖拽/粘贴上传，输出RGBA图像（透明通道内置）"""

    @classmethod
    def define_schema(cls):
        files = _get_input_image_files()

        return io.Schema(
            node_id="AFOLIE加载图片",
            display_name="加载图片 🖼️",
            category="AFOLIE/input",
            description="支持拖拽/粘贴上传，PNG透明通道保留在图像中(4通道)",
            inputs=[
                io.Combo.Input(
                    "image",
                    options=files if files else ["(无图片)"],
                    upload=io.UploadType.image,
                ),
            ],
            outputs=[
                io.Image.Output("图像"),
            ],
        )

    @classmethod
    def execute(cls, image):
        if image.startswith("("):
            raise ValueError("请先上传或选择一张图片")

        file_path = folder_paths.get_annotated_filepath(image, "input")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        img_tensor = _load_rgba_image(file_path)

        channels = img_tensor.shape[3]
        print(f"[AFOLIE加载图片] {image} "
              f"{img_tensor.shape[2]}x{img_tensor.shape[1]} "
              f"{'RGBA' if channels == 4 else 'RGB'}")

        return io.NodeOutput(img_tensor)


class AFOLIEBrowseImage(io.ComfyNode):
    """浏览图片节点 - 纯预览查看节点，连接图像后直接在节点上预览图片"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE浏览图片",
            display_name="浏览图片 🔍",
            category="AFOLIE/output",
            description="图片预览查看节点，连接图像后直接在节点上预览",
            is_output_node=True,
            hidden=[io.Hidden.unique_id],
            inputs=[
                io.Image.Input("图像"),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, 图像, unique_id=None):
        output_dir = folder_paths.get_temp_directory()
        batch_size = 图像.shape[0]
        results = []

        for i in range(batch_size):
            pil_img = tensor2pil(图像[i])

            filename = f"afolie_browse_{unique_id}_{i:04d}.png"
            file_path = os.path.join(output_dir, filename)
            pil_img.save(file_path, format='PNG', compress_level=1)

            results.append({
                "filename": filename,
                "subfolder": "",
                "type": "temp"
            })

        return io.NodeOutput(ui={"images": results})
