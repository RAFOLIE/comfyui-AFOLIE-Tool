"""
AFOLIE 背景透明化节点（V3 API）
将指定颜色的背景转换为透明
"""

import torch
import numpy as np
from PIL import Image

from comfy_api.latest import io
from .utils import tensor2pil, pil2tensor, hex_to_rgb, color_distance, find_edge_connected_regions


class AFOLIEBackgroundTransparent(io.ComfyNode):
    """背景透明化节点 - 将指定颜色的背景转换为透明"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE背景透明化",
            display_name="背景透明化 🎨",
            category="AFOLIE/图像",
            description="将指定颜色的背景转换为透明，支持颜色容差和边缘保护",
            inputs=[
                io.Image.Input("图像"),
                io.String.Input("透明色值", default="#ffffff", multiline=False),
                io.Float.Input("颜色容差", default=10.0, min=0.0, max=100.0, step=0.5),
                io.Boolean.Input("保护主体内部颜色", default=True),
            ],
            outputs=[
                io.Image.Output("图像"),
                io.Mask.Output("遮罩"),
            ],
        )

    @classmethod
    def execute(cls, 图像, 透明色值, 颜色容差, 保护主体内部颜色):
        # 解析目标颜色
        try:
            target_rgb = hex_to_rgb(透明色值)
        except ValueError:
            target_rgb = (255, 255, 255)

        batch_size = 图像.shape[0]

        max_distance = np.sqrt(255**2 * 3)
        threshold = (颜色容差 / 100.0) * max_distance

        result_images = []
        result_masks = []

        for i in range(batch_size):
            img = 图像[i]
            pil_img = tensor2pil(img)
            img_array = np.array(pil_img)

            # 只使用 RGB 通道
            if img_array.ndim == 3 and img_array.shape[2] == 4:
                rgb_array = img_array[:, :, :3]
            else:
                rgb_array = img_array

            distance = color_distance(rgb_array, target_rgb)
            match_mask = distance <= threshold

            if 保护主体内部颜色:
                transparent_mask = find_edge_connected_regions(match_mask)
            else:
                transparent_mask = match_mask

            # 创建 RGBA 图像
            rgba_array = np.zeros((rgb_array.shape[0], rgb_array.shape[1], 4), dtype=np.uint8)
            rgba_array[:, :, :3] = rgb_array
            rgba_array[:, :, 3] = 255
            rgba_array[transparent_mask, 3] = 0

            rgba_pil = Image.fromarray(rgba_array, mode='RGBA')
            rgba_tensor = pil2tensor(rgba_pil)
            result_images.append(rgba_tensor)

            mask_array = (~transparent_mask).astype(np.float32)
            mask_tensor = torch.from_numpy(mask_array).unsqueeze(0)
            result_masks.append(mask_tensor)

        final_image = torch.cat(result_images, dim=0)
        final_mask = torch.cat(result_masks, dim=0)

        return io.NodeOutput(final_image, final_mask)
