# ComfyUI Advanced Camera Prompts

Advanced camera control prompt generator for ComfyUI that reads camera information from 3D nodes and generates precise, professional camera control prompts.

## Features

- **Automatic Camera Detection**: Reads camera position, target, and angles from Load 3D nodes
- **Professional Shot Types**: Automatically classifies shots (extreme close-up, close-up, medium shot, wide shot, etc.)
- **Camera Angle Recognition**: Detects high angle, low angle, bird's eye, dutch angle, and more
- **Focal Length Support**: Calculate FOV from focal length (1-1000mm)
- **Framing-Based Classification**: Optional object scale input for accurate shot type detection
- **Dual Output**: Generates both human-readable prompts and structured JSON data
- **Industry Standard**: Based on cinematography standards for shot types and camera angles

## Installation

1. Clone this repository into your `ComfyUI/custom_nodes/` folder:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/jandan520/ComfyUI-AdvancedCameraPrompts.git
   ```

2. Restart ComfyUI

## Usage

### Node Inputs

**Required:**
- **Camera Info** (`LOAD3D_CAMERA`): Camera information from Load 3D or Load 3D - Animation nodes

**Optional:**
- **Focal Length (mm)** (`FLOAT`, default: 50.0): Camera lens focal length (1-1000mm)
- **Object Scale (meters)** (`FLOAT`, default: 1.0): Object size in meters for framing-based shot classification
- **Custom Description** (`STRING`): Additional text to append to the prompt

### Node Outputs

1. **Prompt** (`STRING`): Human-readable camera control prompt
2. **Camera JSON** (`STRING`): Structured JSON with all camera parameters

## Example Output

**Prompt:**
```
Pan the camera 45 degrees to the right, high angle medium shot (camera distance 2.5 m 50mm FOV 40°)
```

**Camera JSON:**
```json
{
    "camera": {
        "focal_length_mm": 50,
        "sensor_width_mm": 36,
        "sensor_height_mm": 24,
        "distance_m": 2.5,
        "tilt_deg": "tilt down 15.0",
        "pan_deg": "pan to right 45.0",
        "roll_deg": 0.0,
        "shot_type": "medium_shot"
    }
}
```

## Shot Types

The node automatically classifies shots based on distance, focal length, FOV, or framing:

- Extreme Close-Up
- Close-Up
- Medium Close-Up
- Medium Shot
- Medium Long Shot
- Full Shot
- Wide Shot
- Extreme Wide Shot

## Camera Angles

Recognized camera angles:

- Eye Level
- High Angle
- Slight Low Angle
- Standard Low Angle
- Deep Low Angle
- Extreme Low Angle (Worm's Eye)
- Bird's Eye
- Dutch Angle
- Dutch Low Angle

## Technical Details

- **Coordinate System**: Z-axis points at camera, X-axis is horizontal, Y-axis is vertical
- **Sensor Format**: 35mm full-frame equivalent (36mm × 24mm)
- **Distance Scale**: 1 grid unit = 4 meters
- **FOV Calculation**: Uses standard formula: `FOV = 2 × arctan(sensor_dim / (2 × focal_length))`

## Requirements

- ComfyUI (latest versions)
- Python 3.8+
- Load 3D nodes (for camera input)

## License

MIT

## Author

Jianghong Zhu

## Credits

Optimized for use with dx8152's MultiAngle LoRA and similar camera control workflows.
