"""
Advanced Camera Control Prompt Generator for ComfyUI

Author: Jianghong Zhu
License: MIT
"""

from .advanced_camera_control_node import AdvancedCameraControlNode

NODE_CLASS_MAPPINGS = {
    "AdvancedCameraControlNode": AdvancedCameraControlNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedCameraControlNode": "Advanced Camera Control Prompt Generator"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
