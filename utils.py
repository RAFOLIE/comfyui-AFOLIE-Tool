"""
AFOLIE 工具函数 - 共享辅助函数模块
"""

import torch
import numpy as np
from PIL import Image, ImageOps


def tensor2pil(image):
    """将张量转换为 PIL 图像，支持 RGB/RGBA/灰度"""
    img_np = image.cpu().numpy()
    if img_np.ndim == 4:
        img_np = img_np.squeeze(0)
    img_np = np.clip(255. * img_np, 0, 255).astype(np.uint8)

    if img_np.ndim == 3:
        channels = img_np.shape[2]
        if channels == 4:
            return Image.fromarray(img_np, mode='RGBA')
        elif channels == 3:
            return Image.fromarray(img_np, mode='RGB')
        elif channels == 1:
            return Image.fromarray(img_np.squeeze(2), mode='L')
    elif img_np.ndim == 2:
        return Image.fromarray(img_np, mode='L')

    return Image.fromarray(img_np)


def pil2tensor(image):
    """将 PIL 图像转换为张量 (1, H, W, C)"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def hex_to_rgb(hex_color):
    """将十六进制颜色字符串转换为 RGB 元组"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"无效的十六进制颜色: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(img_array, target_rgb):
    """计算图像中每个像素与目标颜色的欧几里得距离"""
    target = np.array(target_rgb, dtype=np.float32)
    diff = img_array.astype(np.float32) - target
    distance = np.sqrt(np.sum(diff ** 2, axis=2))
    return distance


def find_edge_connected_regions(mask):
    """找到与图像边缘连通的区域（使用 scipy）"""
    from scipy import ndimage

    edge_seed = np.zeros_like(mask, dtype=bool)
    edge_seed[0, :] = mask[0, :]
    edge_seed[-1, :] = mask[-1, :]
    edge_seed[:, 0] = mask[:, 0]
    edge_seed[:, -1] = mask[:, -1]

    labeled_array, num_features = ndimage.label(mask)

    edge_labels = set(labeled_array[edge_seed])
    edge_labels.discard(0)

    edge_connected = np.zeros_like(mask, dtype=bool)
    for label in edge_labels:
        edge_connected |= (labeled_array == label)

    return edge_connected


def generate_checkerboard(width, height, cell_size=16):
    """生成棋盘格背景用于透明区域预览"""
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    checker = ((x_coords // cell_size) + (y_coords // cell_size)) % 2
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
        if pil_mask.size != rgba.size:
            pil_mask = pil_mask.resize(rgba.size, Image.NEAREST)
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


def extract_alpha(图像, mask=None):
    """从图像(4通道)或mask中提取alpha通道

    优先级: mask输入 > 图像alpha通道
    Args:
        图像: tensor [B,H,W,C] C=3或4
        mask: optional tensor [B,H,W] 或 [H,W]
    Returns:
        (rgb_tensor [B,H,W,3], alpha_tensor [B,H,W] 或 None)
    """
    batch_size = 图像.shape[0]
    channels = 图像.shape[3] if 图像.dim() == 4 else 3

    # 分离RGB
    if channels == 4:
        rgb = 图像[:, :, :, :3]
        image_alpha = 图像[:, :, :, 3]
    else:
        rgb = 图像
        image_alpha = None

    # 处理mask维度
    if mask is not None:
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        if mask.shape[0] == 1 and batch_size > 1:
            mask = mask.expand(batch_size, -1, -1)

    # mask优先，否则用图像alpha
    alpha = mask if mask is not None else image_alpha
    return rgb, alpha


def resize_image_with_alpha(图像, target_size, pil_filter, mask=None):
    """缩放图像，保留alpha通道（RGBA优先模式）

    Args:
        图像: tensor [B,H,W,C] C=3或4
        target_size: (width, height)
        pil_filter: PIL重采样滤镜
        mask: optional mask tensor [B,H,W]
    Returns:
        (result_tensor [B,H,W,C], mask_tensor [B,H,W])
        result_tensor: RGBA(4ch)有alpha时, RGB(3ch)无alpha时
        mask_tensor: 始终输出，作为备选遮罩
    """
    batch_size = 图像.shape[0]
    target_width, target_height = target_size
    rgb, alpha = extract_alpha(图像, mask)

    resized_images = []
    resized_alphas = []

    for i in range(batch_size):
        # 缩放RGB
        pil_rgb = Image.fromarray(
            np.clip(255. * rgb[i].cpu().numpy(), 0, 255).astype(np.uint8),
            mode='RGB'
        )
        pil_rgb = pil_rgb.resize(target_size, pil_filter)

        # 缩放alpha
        if alpha is not None:
            a = alpha[i] if i < alpha.shape[0] else alpha[0]
            pil_alpha = Image.fromarray(
                np.clip(255. * a.cpu().numpy(), 0, 255).astype(np.uint8),
                mode='L'
            )
            pil_alpha = pil_alpha.resize(target_size, Image.NEAREST)
            pil_rgb.putalpha(pil_alpha)
            resized_alphas.append(
                torch.from_numpy(np.array(pil_alpha).astype(np.float32) / 255.0)
            )

        resized_images.append(
            torch.from_numpy(np.array(pil_rgb).astype(np.float32) / 255.0).unsqueeze(0)
        )

    result = torch.cat(resized_images, dim=0)

    if len(resized_alphas) > 0:
        mask_result = torch.stack(resized_alphas, dim=0)
    else:
        mask_result = torch.ones(
            batch_size, target_height, target_width, dtype=torch.float32
        )

    return result, mask_result
