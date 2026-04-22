"""
AFOLIE 图像文件夹节点（V3 API）
保存图像到自定义文件夹
"""

import os
import torch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths
from datetime import datetime

from comfy_api.latest import io
from ..utils import tensor2pil


class AFOLIEImageFolder(io.ComfyNode):
    """图像文件夹节点 - 将图像保存到指定的自定义文件夹路径"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE图像文件夹",
            display_name="图像文件夹 💾",
            category="AFOLIE/output",
            description="将图像保存到指定的自定义文件夹路径（非默认output文件夹）",
            is_output_node=True,
            inputs=[
                io.Image.Input("图像"),
                io.String.Input("文件夹路径", default="E:/AI/ComfyUI_works/output_custom", multiline=False),
                io.String.Input("文件名前缀", default="AFOLIE", multiline=False),
                io.Combo.Input("文件格式", options=["png", "jpg", "jpeg", "webp"]),
                io.Boolean.Input("保存元数据", default=True, optional=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.String.Output("保存路径"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 文件夹路径, 文件名前缀="AFOLIE", 文件格式="png", 保存元数据=True):
        # 确保文件夹路径存在
        folder_path = 文件夹路径.strip()
        if not folder_path:
            folder_path = "E:/AI/ComfyUI_works/output_custom"

        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"创建文件夹失败: {folder_path}, 错误: {str(e)}")
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "saved_images")
            os.makedirs(folder_path, exist_ok=True)

        if 文件格式 == "jpg":
            文件格式 = "jpeg"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_paths = []
        counter = getattr(cls, '_counter', 0)

        batch_size = 图像.shape[0]

        for i in range(batch_size):
            pil_img = tensor2pil(图像[i])

            filename = f"{文件名前缀}_{timestamp}_{counter:04d}.{文件格式}"
            counter += 1
            file_path = os.path.join(folder_path, filename)

            save_kwargs = {}

            if 文件格式 == "png":
                save_kwargs["compress_level"] = 0
                if 保存元数据:
                    metadata = PngInfo()
                    metadata.add_text("Software", "ComfyUI - AFOLIE")
                    metadata.add_text("Timestamp", timestamp)
                    metadata.add_text("Prefix", 文件名前缀)
                    save_kwargs["pnginfo"] = metadata

            elif 文件格式 in ["jpeg", "jpg"]:
                save_kwargs["quality"] = 100
                save_kwargs["optimize"] = True
                if pil_img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', pil_img.size, (255, 255, 255))
                    if pil_img.mode == 'P':
                        pil_img = pil_img.convert('RGBA')
                    background.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode == 'RGBA' else None)
                    pil_img = background

            elif 文件格式 == "webp":
                save_kwargs["quality"] = 100
                save_kwargs["method"] = 6

            try:
                pil_img.save(file_path, format=文件格式.upper(), **save_kwargs)
                saved_paths.append(file_path)
                print(f"图像已保存: {file_path}")
            except Exception as e:
                print(f"保存图像失败: {file_path}, 错误: {str(e)}")
                saved_paths.append(f"保存失败: {str(e)}")

        cls._counter = counter

        saved_paths_str = "\n".join(saved_paths)
        ui_images = [
            {"filename": os.path.basename(p), "subfolder": "", "type": "output"}
            for p in saved_paths if os.path.exists(p)
        ]

        return io.NodeOutput(图像, saved_paths_str, ui={"images": ui_images})
