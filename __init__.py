"""
AFOLIE Tool - ComfyUI Custom Nodes (V3 API)
"""

from comfy_api.latest import ComfyExtension, io
from typing_extensions import override

from .image_size_node import (
    AFOLIEImagePixelResize,
    AFOLIEImageScaleResize,
    AFOLIEImageGridCrop,
    AFOLIEPixelAlign,
)
from .background_transparent import AFOLIEBackgroundTransparent
from .input.batch_image_loader import (
    AFOLIEInputBatchImages,
    AFOLIEInputBatchImagePixels,
    AFOLIEInputBatchImageScale,
)
from .input.image_loader import AFOLIELoadImage, AFOLIEBrowseImage
from .output.image_folder_node import AFOLIEImageFolder
from .output.transparent_image_node import AFOLIETransparentPreview, AFOLIETransparentSave
from .dynamic_text_node import AFOLIEDynamicText

# Web directory for frontend JavaScript files
WEB_DIRECTORY = "./web"
__all__ = ["WEB_DIRECTORY"]
__version__ = "2.0.0"


class AFOLIEExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            # 图像处理
            AFOLIEImagePixelResize,
            AFOLIEImageScaleResize,
            AFOLIEImageGridCrop,
            AFOLIEPixelAlign,
            AFOLIEBackgroundTransparent,
            # 输入
            AFOLIEInputBatchImages,
            AFOLIEInputBatchImagePixels,
            AFOLIEInputBatchImageScale,
            AFOLIELoadImage,
            # 输出
            AFOLIEBrowseImage,
            AFOLIEImageFolder,
            AFOLIETransparentPreview,
            AFOLIETransparentSave,
            # 文本
            AFOLIEDynamicText,
        ]


async def comfy_entrypoint() -> AFOLIEExtension:
    return AFOLIEExtension()
