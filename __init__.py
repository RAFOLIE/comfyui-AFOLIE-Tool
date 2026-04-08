"""
AFOLIE Image Size - ComfyUI Custom Node
Photoshop-like image resizing functionality
"""

from .image_size_node import NODE_CLASS_MAPPINGS as IMAGE_SIZE_MAPPINGS
from .image_size_node import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_SIZE_DISPLAY_MAPPINGS
from .output import NODE_CLASS_MAPPINGS as OUTPUT_MAPPINGS
from .output import NODE_DISPLAY_NAME_MAPPINGS as OUTPUT_DISPLAY_MAPPINGS
from .input import NODE_CLASS_MAPPINGS as INPUT_MAPPINGS
from .input import NODE_DISPLAY_NAME_MAPPINGS as INPUT_DISPLAY_MAPPINGS
from .background_transparent import NODE_CLASS_MAPPINGS as BG_TRANSPARENT_MAPPINGS
from .background_transparent import NODE_DISPLAY_NAME_MAPPINGS as BG_TRANSPARENT_DISPLAY_MAPPINGS
# Merge all node mappings
NODE_CLASS_MAPPINGS = {
    **IMAGE_SIZE_MAPPINGS,
    **OUTPUT_MAPPINGS,
    **INPUT_MAPPINGS,
    **BG_TRANSPARENT_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **IMAGE_SIZE_DISPLAY_MAPPINGS,
    **OUTPUT_DISPLAY_MAPPINGS,
    **INPUT_DISPLAY_MAPPINGS,
    **BG_TRANSPARENT_DISPLAY_MAPPINGS,
}

# Web directory for frontend JavaScript files
WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
__version__ = "1.0.0"
