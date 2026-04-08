"""
AFOLIE 透明图像节点 - 预览和保存带透明通道的图像
支持将 IMAGE + MASK 合并为 RGBA 图像进行预览和保存
"""

import os
import torch
import numpy as np
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import folder_paths
from datetime import datetime


def tensor2pil(image):
    """Convert tensor to PIL Image"""
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


def generate_checkerboard(width, height, cell_size=16):
    """生成棋盘格背景用于透明区域预览（numpy 向量化，速度快）"""
    # 创建坐标网格
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    # 计算棋盘格图案
    checker = ((x_coords // cell_size) + (y_coords // cell_size)) % 2
    # 浅灰 204, 白色 255
    checkerboard = np.where(
        checker[:, :, np.newaxis] == 0,
        np.array([204, 204, 204], dtype=np.uint8),
        np.array([255, 255, 255], dtype=np.uint8)
    )
    return Image.fromarray(checkerboard, mode='RGB')


def combine_to_rgba(pil_img, pil_mask=None, invert_mask=False):
    """将 RGB 图像和遮罩合并为 RGBA 图像"""
    rgba = pil_img.convert('RGBA')
    if pil_mask is not None:
        # 确保遮罩尺寸匹配
        if pil_mask.size != rgba.size:
            pil_mask = pil_mask.resize(rgba.size, Image.NEAREST)
        # 如果需要反转遮罩
        if invert_mask:
            pil_mask = ImageOps.invert(pil_mask)
        rgba.putalpha(pil_mask)
    return rgba


def mask_to_pil(mask_tensor, invert=False):
    """将 mask 张量转为 PIL 灰度图"""
    if mask_tensor is None:
        return None
    mask_np = np.clip(255. * mask_tensor.cpu().numpy(), 0, 255).astype(np.uint8)
    if invert:
        mask_np = 255 - mask_np
    return Image.fromarray(mask_np, mode='L')


class AFOLIE透明图像预览:
    """
    透明图像预览节点
    接收 IMAGE + MASK，合并为 RGBA 图像并预览（保留透明背景）
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "反转遮罩": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "开启后遮罩白色区域变为透明，黑色区域保留（适用于大多数抠图节点输出的遮罩）"
                }),
            },
            "optional": {
                "mask": ("MASK",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("图像", "遮罩")
    FUNCTION = "preview_image"
    OUTPUT_NODE = True
    CATEGORY = "AFOLIE/output"

    def preview_image(self, 图像, 反转遮罩=True, mask=None, unique_id=None, extra_pnginfo=None):
        """
        预览带透明通道的图像
        
        Args:
            图像: 输入图像张量 [B, H, W, 3]
            mask: 可选的透明遮罩张量 [B, H, W]
        """
        batch_size = 图像.shape[0]
        
        # 处理 mask 维度
        if mask is not None:
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            if mask.shape[0] == 1 and batch_size > 1:
                mask = mask.expand(batch_size, -1, -1)
        
        results = []
        
        for i in range(batch_size):
            # RGB 图像
            pil_img = tensor2pil(图像[i])
            
            # 遮罩（根据反转设置处理）
            pil_mask = None
            if mask is not None:
                pil_mask = mask_to_pil(mask[i] if i < mask.shape[0] else mask[0], invert=反转遮罩)
            
            # 合并为 RGBA（透明背景）
            rgba_img = combine_to_rgba(pil_img, pil_mask)
            
            # 直接保存 RGBA PNG 到临时目录（保留透明背景）
            filename = f"afolie_preview_{i:04d}.png"
            file_path = os.path.join(self.output_dir, filename)
            rgba_img.save(file_path, format='PNG', compress_level=1)
            
            results.append({
                "filename": filename,
                "subfolder": "",
                "type": self.type
            })
        
        # 生成默认全白遮罩（如果没有输入遮罩）
        if mask is None:
            mask_result = torch.ones(
                batch_size, 图像.shape[1], 图像.shape[2],
                dtype=torch.float32
            )
        else:
            mask_result = mask
        
        return {
            "ui": {"images": results},
            "result": (图像, mask_result)
        }


class AFOLIE透明图像保存:
    """
    透明图像保存节点
    接收 IMAGE + MASK，合并为 RGBA 图像并保存为带透明通道的 PNG
    文件命名遵循 ComfyUI 官方规则：ComfyUI_00001_.png
    同时在界面上显示带棋盘格背景的预览
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "反转遮罩": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "开启后遮罩白色区域变为透明，黑色区域保留（适用于大多数抠图节点输出的遮罩）"
                }),
            },
            "optional": {
                "mask": ("MASK",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("图像", "遮罩")
    FUNCTION = "save_image"
    OUTPUT_NODE = True
    CATEGORY = "AFOLIE/output"

    def save_image(self, 图像, 反转遮罩=True, mask=None, unique_id=None, extra_pnginfo=None):
        """
        保存带透明通道的图像为 PNG（文件命名遵循 ComfyUI 官方规则）
        """
        batch_size = 图像.shape[0]
        img_height = 图像.shape[1]
        img_width = 图像.shape[2]
        
        # 使用 ComfyUI 官方的文件路径生成方式
        filename_prefix = "ComfyUI"
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, img_width, img_height
        )
        
        # 处理 mask 维度
        if mask is not None:
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            if mask.shape[0] == 1 and batch_size > 1:
                mask = mask.expand(batch_size, -1, -1)
        
        results = []
        
        # 准备元数据
        metadata = PngInfo()
        if extra_pnginfo is not None:
            for k, v in extra_pnginfo.items():
                metadata.add_text(k, str(v))
        metadata.add_text("Software", "ComfyUI - AFOLIE")
        
        for i in range(batch_size):
            # RGB 图像
            pil_img = tensor2pil(图像[i])
            
            # 遮罩（根据反转设置处理）
            pil_mask = None
            if mask is not None:
                pil_mask = mask_to_pil(mask[i] if i < mask.shape[0] else mask[0], invert=反转遮罩)
            
            # 合并为 RGBA
            rgba_img = combine_to_rgba(pil_img, pil_mask)
            
            # ComfyUI 官方命名格式：{prefix}_{counter:05}_.png
            file = f"{filename}_{counter:05}_.png"
            file_path = os.path.join(full_output_folder, file)
            
            # 保存带透明通道的 PNG
            rgba_img.save(file_path, format='PNG', compress_level=self.compress_level, pnginfo=metadata)
            
            print(f"透明图像已保存: {file_path}")
            counter += 1
            
            # 直接用透明 PNG 作为预览
            preview_filename = f"afolie_preview_{i:04d}.png"
            preview_path = os.path.join(folder_paths.get_temp_directory(), preview_filename)
            rgba_img.save(preview_path, format='PNG', compress_level=1)
            
            results.append({
                "filename": preview_filename,
                "subfolder": "",
                "type": "temp"
            })
        
        # 生成默认全白遮罩（如果没有输入遮罩）
        if mask is None:
            mask_result = torch.ones(
                batch_size, 图像.shape[1], 图像.shape[2],
                dtype=torch.float32
            )
        else:
            mask_result = mask
        
        return {
            "ui": {"images": results},
            "result": (图像, mask_result)
        }


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE透明图像预览": AFOLIE透明图像预览,
    "AFOLIE透明图像保存": AFOLIE透明图像保存
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE透明图像预览": "透明图像预览 👁️",
    "AFOLIE透明图像保存": "透明图像保存 💾"
}