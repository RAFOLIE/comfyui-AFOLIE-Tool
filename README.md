# AFOLIE Tool - ComfyUI Custom Nodes

<div align="center">

**Language / 语言：** [English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>
## English

A comprehensive ComfyUI custom node collection for image processing, built on the **V3 Extension API**. Provides Photoshop-like image resizing, batch image loading, PNG transparency support, background transparency, transparent image preview/save, pixel alignment, and custom folder saving functionality.

### Features Overview

This plugin provides **14 nodes** organized into five categories:

#### Image Processing (AFOLIE/image)
| Node | Description |
|------|-------------|
| **Image Pixel Resize** | Pixel-based image resizing with 7 resampling methods, RGBA alpha passthrough |
| **Image Scale Resize** | Scale-based image resizing (0.01x - 12x), RGBA alpha passthrough |
| **Image Grid Crop** | Split image into grid cells |
| **Pixel Alignment** | Align pixels to perfect grid for pixel art |
| **Background Transparent** | Convert specified color background to transparent |

#### Input Nodes (AFOLIE/input)
| Node | Description |
|------|-------------|
| **Load Image** | Drag & drop image upload, preserves PNG transparency as 4-channel RGBA output |
| **Browse Image** | Pure preview node, displays image with transparency, no output ports |
| **Batch Images** | Load batch images preserving original sizes |
| **Batch Image Pixels** | Load and resize to uniform pixel dimensions |
| **Batch Image Scale** | Load and scale by multiplier |

#### Output Nodes (AFOLIE/output)
| Node | Description |
|------|-------------|
| **Image Folder** | Save images to custom folder paths |
| **Transparent Preview** | Preview images with transparent background (RGBA PNG) |
| **Transparent Save** | Save images as transparent PNG with ComfyUI official naming |

#### Text Nodes (AFOLIE/text)
| Node | Description |
|------|-------------|
| **Dynamic Text** | Dynamic text interface with multi-line input and variable substitution |

### Key Highlights

#### RGBA Alpha Transparency
All image nodes natively support **4-channel RGBA** images - transparency is built into the image tensor itself, not separated into a mask. This provides a seamless workflow for transparent PNG images:
- **Load Image** node outputs RGBA directly from PNG uploads
- Processing nodes (resize, crop, align) preserve alpha channel through operations
- **Browse Image** and **Transparent Preview** render transparency correctly
- Mask I/O remains available as backup for compatibility with official ComfyUI nodes

#### Background Transparent
- Hex color input (#ffffff format)
- Color picker with HSB slider
- Color tolerance slider (0-100%)
- Protect internal colors option

#### Pixel Alignment
- Align pixels to perfect grid
- Fix AI-generated pixel art inconsistencies
- Quantize colors to strict palette
- Preserve details like dithering

### Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RAFOLIE/comfyui-AFOLIE-Tool.git
```

### Requirements

```
torch>=1.9.0
numpy>=1.21.0
Pillow>=8.0.0
scipy>=1.7.0
```

### License

GPL-3.0 License

### Author

AFOLIE

---

<a name="中文"></a>
## 中文

ComfyUI 自定义节点集合，基于 **V3 Extension API** 构建。提供类似 Photoshop 的图像大小调整、批量图像加载、PNG 透明通道支持、背景透明化、透明图像预览/保存、像素对齐和自定义文件夹保存功能。

### 功能概览

本插件提供 **14 个节点**，分为五个类别：

#### 图像处理 (AFOLIE/image)
| 节点 | 说明 |
|------|------|
| **图像像素缩放** | 基于像素的图像大小调整，支持 7 种采样方法，RGBA 透明通道透传 |
| **图像倍数缩放** | 基于倍数的图像缩放 (0.01x - 12x)，RGBA 透明通道透传 |
| **图像网格裁剪** | 将图像分割成网格单元 |
| **像素对齐** | 将像素对齐到完美网格，适用于像素艺术 |
| **背景透明化** | 将指定颜色的背景转换为透明 |

#### 输入节点 (AFOLIE/input)
| 节点 | 说明 |
|------|------|
| **加载图片** | 支持拖拽/粘贴上传图片，PNG 透明通道保留在 4 通道 RGBA 图像输出中 |
| **浏览图片** | 纯预览查看节点，显示带透明通道的图像，无输出端口 |
| **Input 批次图像** | 加载批次图像，保持原始尺寸 |
| **Input 批次图像像素** | 加载并调整到统一像素尺寸 |
| **Input 批次图像倍数** | 加载并按倍数统一缩放 |

#### 输出节点 (AFOLIE/output)
| 节点 | 说明 |
|------|------|
| **图像文件夹** | 保存图像到自定义文件夹路径 |
| **透明图像预览** | 预览带透明背景的图像（RGBA PNG） |
| **透明图像保存** | 保存为带透明通道的 PNG，遵循 ComfyUI 官方命名规则 |

#### 文本节点 (AFOLIE/text)
| 节点 | 说明 |
|------|------|
| **动态文本** | 动态文本界面，支持多行输入和变量替换 |

### 核心亮点

#### RGBA 透明通道
所有图像节点原生支持 **4 通道 RGBA** 图像 —— 透明信息内置在图像张量中，而非分离为遮罩。为透明 PNG 图像提供无缝工作流：
- **加载图片** 节点直接输出 RGBA，PNG 透明通道完整保留
- 处理节点（缩放、裁剪、对齐）在操作中保留 alpha 通道
- **浏览图片** 和 **透明图像预览** 正确渲染透明区域
- 遮罩 I/O 作为备选保留，兼容官方 ComfyUI 节点

#### 背景透明化
- 十六进制颜色输入 (#ffffff 格式)
- 颜色选择器，支持色相立方体和 HSB 滑块
- 颜色容差滑块 (0-100%)
- 保护主体内部颜色选项

#### 像素对齐
- 将像素对齐到完美网格
- 修复 AI 生成像素艺术的不一致
- 量化颜色到严格的调色板
- 保持细节（如抖动）

### 安装方法

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RAFOLIE/comfyui-AFOLIE-Tool.git
```

### 依赖

```
torch>=1.9.0
numpy>=1.21.0
Pillow>=8.0.0
scipy>=1.7.0
```

### 许可证

GPL-3.0 许可证

### 作者

AFOLIE

---

## Version History / 版本历史

### v2.0.0 (2026-04-22)
- V3 Extension API upgrade (ComfyExtension + io.ComfyNode + define_schema)
- RGBA alpha transparency: all image nodes natively support 4-channel RGBA
- Added Load Image node with drag & drop upload, PNG transparency preserved
- Added Browse Image node for preview without output ports
- Added Dynamic Text node
- Shared utils module (tensor2pil, extract_alpha, resize_image_with_alpha)
- Mask I/O retained as backup for official ComfyUI node compatibility

### v1.2.0 (2026-04-08)
- Image Pixel Resize node now supports transparent mask passthrough
- Added Transparent Image Preview node
- Added Transparent Image Save node
- Invert mask option for compatibility

### v1.1.0 (2025-12-19)
- Added Pixel Alignment node
- Added Background Transparent node
- Added Image Grid Crop node

### v1.0.0 (2025-12-13)
- Initial release
- Image Pixel Resize, Image Scale Resize
- Three Input batch nodes
- Image Folder save node

---

<div align="center">

**Made with by AFOLIE**

</div>
