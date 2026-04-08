# AFOLIE Tool - ComfyUI Custom Nodes

<div align="center">

**Language / 语言：** [English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>
## 🇬🇧 English

A comprehensive ComfyUI custom node collection for image processing, providing Photoshop-like image resizing, batch image loading, background transparency, transparent image preview/save, pixel alignment, and custom folder saving functionality.

### 📦 Features Overview

This plugin provides **11 powerful nodes** organized into four categories:

#### 🖼️ Image Processing (AFOLIE/图像)
| Node | Description |
|------|-------------|
| **Image Pixel Resize 📐** | Pixel-based image resizing with 7 resampling methods, supports transparent mask |
| **Image Scale Resize 🔢** | Scale-based image resizing (0.01x - 12x) |
| **Image Grid Crop ✂️** | Split image into grid cells |
| **Pixel Alignment 🎯** | Align pixels to perfect grid for pixel art |
| **Background Transparent 🎨** | Convert specified color background to transparent |

#### 📥 Input Nodes (AFOLIE/input)
| Node | Description |
|------|-------------|
| **Input Batch Images 📁** | Load batch images preserving original sizes |
| **Input Batch Images Pixels 📐** | Load and resize to uniform pixel dimensions |
| **Input Batch Images Scale 🔢** | Load and scale by multiplier |

#### 💾 Output Nodes (AFOLIE/output)
| Node | Description |
|------|-------------|
| **Image Folder 💾** | Save images to custom folder paths |
| **Transparent Image Preview 👁️** | Preview images with transparent background (RGBA PNG) |
| **Transparent Image Save 💾** | Save images as transparent PNG with ComfyUI official naming |

### 📸 Screenshots

![Screenshot 1](images/01.png)
![Screenshot 2](images/02.png)
![Screenshot 3](images/03.png)

### 🎯 Key Features

#### Background Transparent 🎨
- Hex color input (#ffffff format)
- Color picker with HSB slider
- Color tolerance slider (0-100%)
- Protect internal colors option

#### Pixel Alignment 🎯
- Align pixels to perfect grid
- Fix AI-generated pixel art inconsistencies
- Quantize colors to strict palette
- Preserve details like dithering

#### Image Grid Crop ✂️
- Split image into horizontal × vertical grid
- Set 0 to skip that direction (for strips)
- Batch processing support

#### Transparent Image Preview & Save
- Combine IMAGE + MASK into RGBA transparent PNG
- Invert mask option for compatibility with different mask sources
- Preview with transparent background in ComfyUI
- Save follows ComfyUI official naming convention (ComfyUI_00001_.png)

### 📥 Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RAFOLIE/comfyui-AFOLIE-Tool.git
```

### 📋 Requirements

```
torch>=1.9.0
numpy>=1.21.0
Pillow>=8.0.0
scipy>=1.7.0
```

### 📝 License

GPL-3.0 License

### 👤 Author

AFOLIE

---

<a name="中文"></a>
## 🇨🇳 中文

ComfyUI 自定义节点集合，提供类似 Photoshop 的图像大小调整、批量图像加载、背景透明化、透明图像预览/保存、像素对齐和自定义文件夹保存功能。

### 📦 功能概览

本插件提供 **11 个强大的节点**，分为三个类别：

#### 🖼️ 图像处理 (AFOLIE/图像)
| 节点 | 说明 |
|------|------|
| **图像像素缩放 📐** | 基于像素的图像大小调整，支持 7 种采样方法，支持透明遮罩透传 |
| **图像倍数缩放 🔢** | 基于倍数的图像缩放 (0.01x - 12x) |
| **图像网格裁剪 ✂️** | 将图像分割成网格单元 |
| **像素对齐 🎯** | 将像素对齐到完美网格，适用于像素艺术 |
| **背景透明化 🎨** | 将指定颜色的背景转换为透明 |

#### 📥 输入节点 (AFOLIE/input)
| 节点 | 说明 |
|------|------|
| **Input批次图像 📁** | 加载批次图像，保持原始尺寸 |
| **Input批次图像像素 📐** | 加载并调整到统一像素尺寸 |
| **Input批次图像倍数 🔢** | 加载并按倍数统一缩放 |

#### 💾 输出节点 (AFOLIE/output)
| 节点 | 说明 |
|------|------|
| **图像文件夹 💾** | 保存图像到自定义文件夹路径 |
| **透明图像预览 👁️** | 预览带透明背景的图像（RGBA PNG） |
| **透明图像保存 💾** | 保存为带透明通道的 PNG，遵循 ComfyUI 官方命名规则 |

### 📸 截图

![截图 1](images/01.png)
![截图 2](images/02.png)
![截图 3](images/03.png)

### 🎯 主要功能

#### 背景透明化 🎨
- 十六进制颜色输入 (#ffffff 格式)
- 颜色选择器，支持色相立方体和 HSB 滑块
- 颜色容差滑块 (0-100%)
- 保护主体内部颜色选项

#### 像素对齐 🎯
- 将像素对齐到完美网格
- 修复 AI 生成像素艺术的不一致
- 量化颜色到严格的调色板
- 保持细节（如抖动）

#### 图像网格裁剪 ✂️
- 将图像分割成 横向 × 纵向 网格
- 设置 0 跳过该方向（用于裁剪长条）
- 支持批量处理

#### 透明图像预览与保存
- 将 IMAGE + MASK 合并为 RGBA 透明 PNG
- 反转遮罩选项，兼容不同来源的遮罩
- 预览时保留透明背景
- 保存遵循 ComfyUI 官方命名规则（ComfyUI_00001_.png）

### 📥 安装方法

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RAFOLIE/comfyui-AFOLIE-Tool.git
```

### 📋 依赖

```
torch>=1.9.0
numpy>=1.21.0
Pillow>=8.0.0
scipy>=1.7.0
```

### 📝 许可证

GPL-3.0 许可证

### 👤 作者

AFOLIE

---

## 📋 Version History / 版本历史

### v1.2.0 (2026-04-08)
- ✅ Image Pixel Resize node now supports transparent mask passthrough (图像像素缩放支持透明遮罩透传)
- ✅ Added Transparent Image Preview node (透明图像预览 👁️)
- ✅ Added Transparent Image Save node (透明图像保存 💾)
- ✅ Invert mask option for compatibility (反转遮罩选项)

### v1.1.0 (2025-12-19)
- ✅ Added Pixel Alignment node (像素对齐)
- ✅ Added Background Transparent node (背景透明化)
- ✅ Added Image Grid Crop node (图像网格裁剪)

### v1.0.0 (2025-12-13)
- ✅ Initial release
- ✅ Image Pixel Resize node
- ✅ Image Scale Resize node
- ✅ Three Input batch nodes
- ✅ Image Folder save node

---

<div align="center">

**Made with ❤️ by AFOLIE**

</div>