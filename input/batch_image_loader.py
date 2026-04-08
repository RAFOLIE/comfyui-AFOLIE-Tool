"""
AFOLIE Input批次图像节点 - 从指定文件夹加载批次图像
提供三种不同的加载方式
"""

import os
import torch
import numpy as np
from PIL import Image
import folder_paths


def pil2tensor(image):
    """Convert PIL Image to tensor"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


class AFOLIEInput批次图像:
    """
    Input批次图像节点 - 单张输出版
    从指定文件夹路径逐张加载图像（保持原始尺寸）
    配合ComfyUI的批处理功能，每次输出一张图像
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "路径": ("STRING", {
                    "default": "E:/AI/ComfyUI_works/input_images",
                    "multiline": False
                }),
                "文件格式": (["all", "png", "jpg"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像",)
    FUNCTION = "load_images"
    CATEGORY = "AFOLIE/input"
    OUTPUT_IS_LIST = (True,)

    def load_images(self, 路径, 文件格式="all"):
        """
        从指定文件夹逐张加载图像（保持原始尺寸）
        返回图像列表，ComfyUI会自动进行批处理
        """
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 根据文件格式筛选文件
        if 文件格式 == "png":
            valid_extensions = ['.png']
        elif 文件格式 == "jpg":
            valid_extensions = ['.jpg', '.jpeg']
        else:
            valid_extensions = ['.png', '.jpg', '.jpeg']
        
        # 获取所有图像文件
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
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 加载所有图像到列表
        loaded_images = []
        
        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                _, ext = os.path.splitext(img_path.lower())
                
                # 根据格式处理图像
                if ext == '.png':
                    if pil_img.mode == 'RGBA':
                        pass
                    elif pil_img.mode == 'RGB':
                        pil_img = pil_img.convert('RGBA')
                    elif pil_img.mode in ('L', 'LA', 'P'):
                        pil_img = pil_img.convert('RGBA')
                    else:
                        pil_img = pil_img.convert('RGBA')
                    
                elif ext in ['.jpg', '.jpeg']:
                    if pil_img.mode == 'RGBA':
                        background = Image.new('RGB', pil_img.size, (255, 255, 255))
                        background.paste(pil_img, mask=pil_img.split()[3])
                        pil_img = background
                    elif pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    pil_img = pil_img.convert('RGBA')
                
                img_tensor = pil2tensor(pil_img)
                loaded_images.append(img_tensor)
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)}")
                
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue
        
        if not loaded_images:
            print("没有成功加载任何图像")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        image_count = len(loaded_images)
        print(f"成功加载 {image_count} 张图像，将逐张输出")
        
        # 返回图像列表，ComfyUI会自动批处理
        return (loaded_images,)


class AFOLIEInput批次图像像素:
    """
    Input批次图像像素节点
    从指定文件夹加载批次图像，并统一调整到指定像素尺寸
    逐张输出，配合ComfyUI的批处理功能
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "路径": ("STRING", {
                    "default": "E:/AI/ComfyUI_works/input_images",
                    "multiline": False
                }),
                "文件格式": (["all", "png", "jpg"],),
                "统一宽度": ("INT", {
                    "default": 512,
                    "min": 64,
                    "max": 8192,
                    "step": 64
                }),
                "统一高度": ("INT", {
                    "default": 512,
                    "min": 64,
                    "max": 8192,
                    "step": 64
                }),
                "采样方法": (["保留细节(Lanczos)", "两次立方(Bicubic)", "两次线性(Bilinear)", "邻近(Nearest)"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像",)
    FUNCTION = "load_images"
    CATEGORY = "AFOLIE/input"
    OUTPUT_IS_LIST = (True,)

    def load_images(self, 路径, 文件格式="all", 统一宽度=512, 统一高度=512, 采样方法="保留细节(Lanczos)"):
        """
        从指定文件夹加载批次图像，并统一调整到指定像素尺寸
        """
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 根据文件格式筛选文件
        if 文件格式 == "png":
            valid_extensions = ['.png']
        elif 文件格式 == "jpg":
            valid_extensions = ['.jpg', '.jpeg']
        else:
            valid_extensions = ['.png', '.jpg', '.jpeg']
        
        # 获取所有图像文件
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
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 映射采样方法到PIL常量
        resample_map = {
            "保留细节(Lanczos)": Image.LANCZOS,
            "两次立方(Bicubic)": Image.BICUBIC,
            "两次线性(Bilinear)": Image.BILINEAR,
            "邻近(Nearest)": Image.NEAREST
        }
        resample_filter = resample_map.get(采样方法, Image.LANCZOS)
        
        target_size = (统一宽度, 统一高度)
        loaded_images = []
        resized_count = 0
        
        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                original_size = pil_img.size
                _, ext = os.path.splitext(img_path.lower())
                
                # 根据格式处理图像
                if ext == '.png':
                    if pil_img.mode == 'RGBA':
                        pass
                    elif pil_img.mode == 'RGB':
                        pil_img = pil_img.convert('RGBA')
                    elif pil_img.mode in ('L', 'LA', 'P'):
                        pil_img = pil_img.convert('RGBA')
                    else:
                        pil_img = pil_img.convert('RGBA')
                    
                elif ext in ['.jpg', '.jpeg']:
                    if pil_img.mode == 'RGBA':
                        background = Image.new('RGB', pil_img.size, (255, 255, 255))
                        background.paste(pil_img, mask=pil_img.split()[3])
                        pil_img = background
                    elif pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    pil_img = pil_img.convert('RGBA')
                
                # 调整到统一尺寸
                # 调整到统一尺寸
                pil_img = pil_img.resize(target_size, resample_filter)
                if original_size != target_size:
                    resized_count += 1
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)} ({original_size[0]}x{original_size[1]} -> {target_size[0]}x{target_size[1]})")
                
                img_tensor = pil2tensor(pil_img)
                loaded_images.append(img_tensor)
                
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue
        
        if not loaded_images:
            print("没有成功加载任何图像")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        image_count = len(loaded_images)
        print(f"成功加载 {image_count} 张图像 (其中 {resized_count} 张已调整尺寸到 {target_size[0]}x{target_size[1]})，将逐张输出")
        
        return (loaded_images,)


class AFOLIEInput批次图像倍数:
    """
    Input批次图像倍数节点
    从指定文件夹加载批次图像，并按倍数统一缩放
    逐张输出，配合ComfyUI的批处理功能
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "路径": ("STRING", {
                    "default": "E:/AI/ComfyUI_works/input_images",
                    "multiline": False
                }),
                "文件格式": (["all", "png", "jpg"],),
                "倍数": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 12.0,
                    "step": 0.01
                }),
                "采样方法": (["保留细节(Lanczos)", "两次立方(Bicubic)", "两次线性(Bilinear)", "邻近(Nearest)"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像",)
    FUNCTION = "load_images"
    CATEGORY = "AFOLIE/input"
    OUTPUT_IS_LIST = (True,)

    def load_images(self, 路径, 文件格式="all", 倍数=1.0, 采样方法="保留细节(Lanczos)"):
        """
        从指定文件夹加载批次图像，并按倍数统一缩放
        所有图像会按照第一张图像的尺寸作为基准进行倍数缩放
        """
        folder_path = 路径.strip()
        if not folder_path or not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 根据文件格式筛选文件
        if 文件格式 == "png":
            valid_extensions = ['.png']
        elif 文件格式 == "jpg":
            valid_extensions = ['.jpg', '.jpeg']
        else:
            valid_extensions = ['.png', '.jpg', '.jpeg']
        
        # 获取所有图像文件
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
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        if not image_files:
            print(f"未找到符合条件的图像文件: {folder_path}")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        # 映射采样方法到PIL常量
        resample_map = {
            "保留细节(Lanczos)": Image.LANCZOS,
            "两次立方(Bicubic)": Image.BICUBIC,
            "两次线性(Bilinear)": Image.BILINEAR,
            "邻近(Nearest)": Image.NEAREST
        }
        resample_filter = resample_map.get(采样方法, Image.LANCZOS)
        
        # 先加载第一张图像获取基准尺寸
        first_img = Image.open(image_files[0])
        base_width, base_height = first_img.size
        target_width = int(base_width * 倍数)
        target_height = int(base_height * 倍数)
        target_width = max(1, target_width)
        target_height = max(1, target_height)
        target_size = (target_width, target_height)
        
        print(f"基准尺寸: {base_width}x{base_height}, 倍数: {倍数}, 目标尺寸: {target_width}x{target_height}")
        
        loaded_images = []
        
        for idx, img_path in enumerate(image_files):
            try:
                pil_img = Image.open(img_path)
                original_size = pil_img.size
                _, ext = os.path.splitext(img_path.lower())
                
                # 根据格式处理图像
                if ext == '.png':
                    if pil_img.mode == 'RGBA':
                        pass
                    elif pil_img.mode == 'RGB':
                        pil_img = pil_img.convert('RGBA')
                    elif pil_img.mode in ('L', 'LA', 'P'):
                        pil_img = pil_img.convert('RGBA')
                    else:
                        pil_img = pil_img.convert('RGBA')
                    
                elif ext in ['.jpg', '.jpeg']:
                    if pil_img.mode == 'RGBA':
                        background = Image.new('RGB', pil_img.size, (255, 255, 255))
                        background.paste(pil_img, mask=pil_img.split()[3])
                        pil_img = background
                    elif pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    pil_img = pil_img.convert('RGBA')
                
                # 调整到目标尺寸
                pil_img = pil_img.resize(target_size, resample_filter)
                print(f"已加载图像 [{idx+1}/{len(image_files)}]: {os.path.basename(img_path)} ({original_size[0]}x{original_size[1]} -> {target_size[0]}x{target_size[1]})")
                
                img_tensor = pil2tensor(pil_img)
                loaded_images.append(img_tensor)
                
            except Exception as e:
                print(f"加载图像失败: {img_path}, 错误: {str(e)}")
                continue
        
        if not loaded_images:
            print("没有成功加载任何图像")
            empty_image = torch.zeros((1, 64, 64, 3))
            return ([empty_image],)
        
        image_count = len(loaded_images)
        print(f"成功加载 {image_count} 张图像 (全部缩放到 {target_size[0]}x{target_size[1]})，将逐张输出")
        
        return (loaded_images,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIEInput批次图像": AFOLIEInput批次图像,
    "AFOLIEInput批次图像像素": AFOLIEInput批次图像像素,
    "AFOLIEInput批次图像倍数": AFOLIEInput批次图像倍数
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIEInput批次图像": "Input批次图像 📁",
    "AFOLIEInput批次图像像素": "Input批次图像像素 📐",
    "AFOLIEInput批次图像倍数": "Input批次图像倍数 🔢"
}
