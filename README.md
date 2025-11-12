# ComfyUI Advanced Camera Prompts

Advanced camera control prompt generator for ComfyUI, optimized for dx8152's MultiAngle LoRA. A ComfyUI custom node that automatically generates professional camera control prompts by analyzing 3D camera data. This node reads camera information from Load 3D nodes and converts it into detailed, cinematography-accurate descriptions suitable for image generation workflows.

## What It Does

This node takes camera position and orientation data from your 3D scene and automatically generates:
- Professional shot type classifications (close-up, medium shot, wide shot, etc.)
- Camera angle descriptions (high angle, low angle, bird's eye, etc.)
- Camera movement and positioning information
- Technical camera parameters (focal length, FOV, distance)

All of this is output as both human-readable prompts and structured JSON data.

## Features

- **Smart Camera Analysis**: Automatically extracts camera position, target, and rotation from 3D nodes
- **Intelligent Shot Classification**: Determines shot types using distance, focal length, FOV, or object framing
- **Angle Detection**: Recognizes various camera angles including high/low angles, dutch angles, and special views
- **Flexible Input**: Supports custom focal length settings and optional object scale for precise framing calculations
- **Dual Output Format**: Provides both natural language prompts and structured JSON data
- **Cinematography Standards**: Based on industry-standard shot types and camera angle definitions

## Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/jandan520/ComfyUI-AdvancedCameraPrompts.git
   ```

3. Restart ComfyUI to load the new node

## How to Use

### Connecting the Node

1. Add a **Load 3D** or **Load 3D - Animation** node to your workflow
2. Add the **Advanced Camera Control Prompt Generator** node
3. Connect the camera output from your 3D node to the "Camera Info" input

### Input Parameters

**Required:**
- **Camera Info**: Connect the camera output from your Load 3D node

**Optional:**
- **Focal Length (mm)**: Set your camera's focal length (default: 50mm, range: 1-1000mm)
  - This affects FOV calculation and shot type classification
- **Object Scale (meters)**: Specify the size of your subject in meters (default: 1.0m)
  - Enables framing-based shot classification for more accurate results
- **Custom Description**: Add any additional text to append to the generated prompt

### Outputs

The node provides two outputs:

1. **Prompt** (String): A natural language description of the camera setup
   - Example: `Pan the camera 45 degrees to the right, high angle medium shot (camera distance 2.5 m 50mm FOV 40°)`

2. **Camera JSON** (String): Structured data with all camera parameters
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

## Shot Type Classification

The node automatically determines shot types based on multiple factors:

| Shot Type | Typical Distance | Focal Length Range | FOV Range |
|-----------|------------------|-------------------|-----------|
| Extreme Close-Up | 0.3-0.6m | 85-135mm | 10-20° |
| Close-Up | 0.6-1.2m | 50-85mm | 20-30° |
| Medium Close-Up | 1.0-1.8m | 35-50mm | 30-40° |
| Medium Shot | 1.5-3.0m | 28-50mm | 35-45° |
| Medium Long Shot | 2.5-4.0m | 24-35mm | 45-55° |
| Full Shot | 3.0-5.0m | 24-35mm | 50-60° |
| Wide Shot | 5.0-10.0m | 18-24mm | 60-90° |
| Extreme Wide Shot | 10-50m | 14-20mm | 90-120° |

## Camera Angles

The node recognizes these camera angles:

- **Eye Level**: Neutral perspective (-5° to +5°)
- **High Angle**: Camera looking down (-20° to -45°)
- **Slight Low Angle**: Just below eye level (5° to 15°)
- **Standard Low Angle**: Waist-chest level (15° to 30°)
- **Deep Low Angle**: Knee-waist level (30° to 45°)
- **Extreme Low Angle**: Ground level, worm's-eye view (45° to 90°)
- **Bird's Eye**: Directly overhead (-80° to -90°)
- **Dutch Angle**: Camera tilted sideways (5° to 30° roll)
- **Dutch Low Angle**: Combination of low angle and roll

## Use Cases

- **Image Generation**: Generate accurate camera prompts for AI image models
- **3D to 2D Workflows**: Convert 3D camera setups into 2D image generation prompts
- **Cinematography Analysis**: Analyze and document camera setups from 3D scenes
- **Workflow Automation**: Automatically generate camera descriptions for batch processing

## Technical Specifications

- **Coordinate System**: Z-axis points toward camera, X-axis is horizontal, Y-axis is vertical
- **Sensor Format**: 35mm full-frame equivalent (36mm × 24mm)
- **Distance Scaling**: 1 grid unit = 4 meters
- **FOV Formula**: `FOV = 2 × arctan(sensor_dimension / (2 × focal_length))`

## Requirements

- ComfyUI (latest version recommended)
- Python 3.8 or higher
- Load 3D nodes (for providing camera input)

## License

MIT License

## Author

Jianghong Zhu
