"""
Advanced Camera Control Prompt Generator
Reads camera information from Load 3D nodes and generates precise camera control prompts.

Author: Jianghong Zhu
"""

import math


class AdvancedCameraControlNode:
    """Advanced camera control prompt generator for ComfyUI."""
    
    EYE_LEVEL_HEIGHT = 0.425
    DEFAULT_POSITION = {"x": 0.0, "y": EYE_LEVEL_HEIGHT, "z": 0.5}
    DEFAULT_TARGET = {"x": 0.0, "y": EYE_LEVEL_HEIGHT, "z": 0.0}
    GRID_TO_METERS = 4.0
    
    SENSOR_WIDTH_MM = 36.0
    SENSOR_HEIGHT_MM = 24.0
    
    FRAMING_THRESHOLDS = {
        "extreme close-up": (90, 1000),
        "close-up": (60, 90),
        "medium close-up": (45, 60),
        "medium shot": (30, 60),
        "medium long shot": (20, 30),
        "full shot": (15, 30),
        "wide shot": (5, 15),
        "extreme wide shot": (0, 5),
    }
    
    CAMERA_SHOTS = [
        {"name": "Extreme Close-Up", "distance_m": [0.3, 0.6], "focal_length_mm": [85, 135], "fov_deg": [10, 20]},
        {"name": "Close-Up", "distance_m": [0.6, 1.2], "focal_length_mm": [50, 85], "fov_deg": [20, 30]},
        {"name": "Medium Close-Up", "distance_m": [1.0, 1.8], "focal_length_mm": [35, 50], "fov_deg": [30, 40]},
        {"name": "Medium Shot", "distance_m": [1.5, 3.0], "focal_length_mm": [28, 50], "fov_deg": [35, 45]},
        {"name": "Medium Long Shot", "distance_m": [2.5, 4.0], "focal_length_mm": [24, 35], "fov_deg": [45, 55]},
        {"name": "Full Shot", "distance_m": [3.0, 5.0], "focal_length_mm": [24, 35], "fov_deg": [50, 60]},
        {"name": "Wide Shot", "distance_m": [5.0, 10.0], "focal_length_mm": [18, 24], "fov_deg": [60, 90]},
        {"name": "Extreme Wide Shot", "distance_m": [10, 50], "focal_length_mm": [14, 20], "fov_deg": [90, 120]},
    ]
    
    CAMERA_ANGLES = [
        {"name": "Eye Level", "tilt_deg": [-5, 5]},
        {"name": "High Angle", "tilt_deg": [-20, -45]},
        {"name": "Slight Low Angle", "tilt_deg": [5, 15]},
        {"name": "Standard Low Angle", "tilt_deg": [15, 30]},
        {"name": "Deep Low Angle", "tilt_deg": [30, 45]},
        {"name": "Extreme Low Angle", "tilt_deg": [45, 90]},
        {"name": "Bird's Eye", "tilt_deg": [-80, -90]},
        {"name": "Dutch Angle", "roll_deg": [5, 30]},
        {"name": "Dutch Low Angle", "roll_deg": [10, 45]},
    ]
    
    EYE_LEVEL_TOLERANCE = 5.0
    DUTCH_ANGLE_ROLL_MIN = 5.0
    HIGH_ANGLE_MIN = 15.0
    BIRD_EYE_MIN = 75.0
    LOW_ANGLE_MAX = -15.0
    WORM_EYE_MAX = -75.0
    
    EXTREME_CLOSE_UP_MAX = 0.6
    CLOSE_UP_MAX = 1.2
    MEDIUM_SHOT_MAX = 3.0
    FULL_SHOT_MAX = 5.0
    WIDE_SHOT_MAX = 10.0
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "camera_info": ("LOAD3D_CAMERA", {"label": "Camera Info (from Load 3D)"}),
            },
            "optional": {
                "focal_length_mm": ("FLOAT", {
                    "default": 50.0,
                    "min": 1.0,
                    "max": 1000.0,
                    "step": 1.0,
                    "label": "Focal Length (mm)"
                }),
                "object_scale_meters": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 100.0,
                    "step": 0.01,
                    "label": "Object Scale (meters)"
                }),
                "custom_description": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "Custom Description (optional)"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "camera_json")
    FUNCTION = "generate_prompt"
    CATEGORY = "prompt/camera"
    
    def generate_prompt(self, camera_info, focal_length_mm=50.0, object_scale_meters=None, custom_description=""):
        """Generate camera control prompt from camera_info"""
        if not camera_info:
            return ("", "{}")
        
        position = camera_info.get("position", {})
        target = camera_info.get("target", {})
        zoom = camera_info.get("zoom", 1)
        
        distance = self._calculate_distance(position, target)
        distance_meters = distance * self.GRID_TO_METERS
        pitch, yaw, roll = self._calculate_camera_angles(position, target)
        
        fov = self._calculate_fov_from_focal_length(focal_length_mm, use_horizontal=True)
        
        angle_type = None
        if abs(pitch) > self.EYE_LEVEL_TOLERANCE:
            angle_type = self._get_angle_type_name(pitch, roll)
        
        shot_prompt = self._get_shot_type_prompt(distance, zoom, fov, focal_length_mm, object_scale_meters)
        position_prompt = self._get_camera_position_prompt(position, target, pitch, yaw)
        
        prompt_parts = []
        description_parts = []
        
        camera_position_text = position_prompt if position_prompt else None
        
        vertical_angle_text = None
        if abs(pitch) > self.EYE_LEVEL_TOLERANCE and angle_type:
            pitch_deg = int(abs(pitch))
            vertical_angle_text = f"tilt down at {pitch_deg} degree" if pitch > 0 else f"tilt up at {pitch_deg} degree"
        
        shot_type_name = None
        camera_info_text = None
        if shot_prompt:
            if "(" in shot_prompt:
                shot_type_name = shot_prompt.split("(")[0].strip()
                camera_info_text = "(" + shot_prompt.split("(")[1].strip()
            else:
                shot_type_name = shot_prompt.strip()
        
        movement_parts = []
        if camera_position_text:
            movement_parts.append(camera_position_text)
        if vertical_angle_text:
            movement_parts.append(vertical_angle_text)
        
        angle_shot_parts = []
        if angle_type:
            angle_shot_parts.append(angle_type)
        if shot_type_name:
            angle_shot_parts.append(shot_type_name)
        
        if movement_parts:
            movement_str = " and ".join(movement_parts)
            if angle_shot_parts:
                angle_shot_str = " ".join(angle_shot_parts)
                description_parts.append(f"{movement_str}, {angle_shot_str}")
            else:
                description_parts.append(f"{movement_str}.")
        elif angle_shot_parts:
            angle_shot_str = " ".join(angle_shot_parts)
            description_parts.append(f"{angle_shot_str}.")
        
        if description_parts:
            prompt_parts.append(" ".join(description_parts))
        
        if camera_info_text:
            prompt_parts.append(camera_info_text)
        
        if custom_description and custom_description.strip():
            prompt_parts.append(custom_description.strip())
        
        final_prompt = " ".join(prompt_parts)
        
        camera_json = self._generate_camera_json(
            position, target, pitch, yaw, roll, distance_meters, 
            focal_length_mm, fov, shot_type_name
        )
        
        return (final_prompt, camera_json)
    
    def _generate_camera_json(self, position, target, pitch, yaw, roll, distance_meters, 
                              focal_length_mm, fov, shot_type_name):
        """Generate JSON format for camera information"""
        import json
        
        shot_type_json = None
        if shot_type_name:
            shot_type_json = shot_type_name.replace(" ", "_").replace("-", "_").lower()
        
        tilt_deg_value = round(pitch, 1)
        if pitch > 0:
            tilt_deg_str = f"tilt down {abs(tilt_deg_value)}"
        elif pitch < 0:
            tilt_deg_str = f"tilt up {abs(tilt_deg_value)}"
        else:
            tilt_deg_str = f"tilt {tilt_deg_value}"
        
        pan_deg_value = round(yaw, 1)
        if yaw > 0:
            pan_deg_str = f"pan to right {abs(pan_deg_value)}"
        elif yaw < 0:
            pan_deg_str = f"pan to left {abs(pan_deg_value)}"
        else:
            pan_deg_str = f"pan {pan_deg_value}"
        
        camera_data = {
            "focal_length_mm": int(focal_length_mm) if focal_length_mm else None,
            "sensor_width_mm": int(self.SENSOR_WIDTH_MM),
            "sensor_height_mm": int(self.SENSOR_HEIGHT_MM),
            "distance_m": round(distance_meters, 2),
            "tilt_deg": tilt_deg_str,
            "pan_deg": pan_deg_str,
            "roll_deg": round(roll, 1),
            "shot_type": shot_type_json
        }
        
        return json.dumps({"camera": camera_data}, indent=4)
    
    def _calculate_distance(self, position, target):
        """Calculate 3D distance from camera position to target"""
        if not position or not target:
            return 0
        
        dx = position.get("x", 0) - target.get("x", 0)
        dy = position.get("y", 0) - target.get("y", 0)
        dz = position.get("z", 0) - target.get("z", 0)
        
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def _calculate_camera_angles(self, position, target):
        """Calculate camera angles: pitch (vertical), yaw (horizontal), roll (rotation)"""
        if not position or not target:
            return (0, 0, 0)
        
        pos_x = position.get("x", 0)
        pos_y = position.get("y", 0)
        pos_z = position.get("z", 0)
        
        tgt_x = target.get("x", 0)
        tgt_y = target.get("y", 0)
        tgt_z = target.get("z", 0)
        
        dx = pos_x - tgt_x
        dy = pos_y - tgt_y
        dz = pos_z - tgt_z
        
        horizontal_dist = math.sqrt(dx * dx + dz * dz)
        
        if horizontal_dist > 0.001:
            pitch_rad = math.atan2(dy, horizontal_dist)
            pitch = math.degrees(pitch_rad)
        else:
            pitch = 90.0 if dy > 0 else -90.0
        
        if abs(dz) > 0.001:
            yaw_rad = math.atan2(dx, -dz)
            yaw = math.degrees(yaw_rad)
        else:
            yaw = 0.0
        
        roll = 0.0
        
        return (pitch, yaw, roll)
    
    def _get_angle_type_name(self, pitch, roll):
        """Get angle type name"""
        if abs(roll) >= 10 and pitch < 0:
            for angle in self.CAMERA_ANGLES:
                if angle["name"] == "Dutch Low Angle" and "roll_deg" in angle:
                    roll_range = angle["roll_deg"]
                    if roll_range[0] <= abs(roll) <= roll_range[1]:
                        return "dutch low angle"
        
        if abs(roll) >= self.DUTCH_ANGLE_ROLL_MIN:
            return "dutch angle"
        
        for angle in self.CAMERA_ANGLES:
            if "tilt_deg" in angle:
                tilt_range = angle["tilt_deg"]
                tilt_value = -pitch
                
                if tilt_range[0] <= tilt_value <= tilt_range[1]:
                    angle_name = angle["name"]
                    if angle_name == "High Angle":
                        return "high angle"
                    elif angle_name == "Slight Low Angle":
                        return "slight low angle"
                    elif angle_name == "Standard Low Angle":
                        return "standard low angle"
                    elif angle_name == "Deep Low Angle":
                        return "deep low angle"
                    elif angle_name == "Extreme Low Angle":
                        return "extreme low angle"
                    elif angle_name == "Bird's Eye":
                        return "bird's eye view"
        
        if pitch >= self.BIRD_EYE_MIN:
            return "bird's eye view"
        elif pitch >= self.HIGH_ANGLE_MIN:
            return "high angle"
        elif pitch <= self.WORM_EYE_MAX:
            return "extreme low angle"
        elif pitch <= -45:
            return "deep low angle"
        elif pitch <= -30:
            return "standard low angle"
        elif pitch <= -15:
            return "slight low angle"
        elif pitch > 0:
            return "high angle"
        else:
            return "low angle"
    
    def _estimate_fov_from_distance(self, distance):
        """Estimate FOV based on distance"""
        distance_meters = distance * self.GRID_TO_METERS
        
        if distance_meters < self.EXTREME_CLOSE_UP_MAX:
            return 15.0
        elif distance_meters < self.CLOSE_UP_MAX:
            return 25.0
        elif distance_meters < self.MEDIUM_SHOT_MAX:
            return 37.5
        elif distance_meters < self.FULL_SHOT_MAX:
            return 52.5
        elif distance_meters < self.WIDE_SHOT_MAX:
            return 70.0
        else:
            return 100.0
    
    def _calculate_fov_from_focal_length(self, focal_length_mm, use_horizontal=True):
        """Calculate FOV from focal length"""
        if focal_length_mm <= 0:
            return None
        
        sensor_dim = self.SENSOR_WIDTH_MM if use_horizontal else self.SENSOR_HEIGHT_MM
        fov_rad = 2.0 * math.atan(sensor_dim / (2.0 * focal_length_mm))
        return math.degrees(fov_rad)
    
    def _estimate_focal_length(self, fov):
        """Estimate focal length from FOV"""
        if fov and fov > 0:
            fov_rad = math.radians(fov)
            focal_length = 18.0 / math.tan(fov_rad / 2.0)
            return max(14.0, min(200.0, focal_length))
        return None
    
    def _calculate_framing_shot_type(self, object_scale_meters, distance_meters, focal_length_mm, use_horizontal=False):
        """Calculate shot type based on framing"""
        if object_scale_meters is None or object_scale_meters <= 0:
            return None
        if distance_meters <= 0 or focal_length_mm <= 0:
            return None
        
        projected_mm = focal_length_mm * (object_scale_meters / distance_meters)
        sensor_dim_mm = self.SENSOR_WIDTH_MM if use_horizontal else self.SENSOR_HEIGHT_MM
        percent_of_frame = 100.0 * projected_mm / sensor_dim_mm
        
        for shot_name, (min_pct, max_pct) in self.FRAMING_THRESHOLDS.items():
            if min_pct <= percent_of_frame < max_pct or (max_pct >= 1000 and percent_of_frame >= min_pct):
                return shot_name
        
        if percent_of_frame >= 100:
            return "extreme close-up"
        elif percent_of_frame < 0.1:
            return "extreme wide shot"
        
        return None
    
    def _get_shot_type_prompt(self, distance, zoom, fov=None, focal_length_mm=None, object_scale_meters=None):
        """Generate shot type prompt"""
        distance_meters = distance * self.GRID_TO_METERS
        distance_str = f"{distance_meters:.1f} m"
        
        estimated_focal = focal_length_mm
        if estimated_focal is None and fov is not None:
            estimated_focal = self._estimate_focal_length(fov)
        
        shot_type = None
        if object_scale_meters is not None and estimated_focal is not None:
            shot_type = self._calculate_framing_shot_type(
                object_scale_meters=object_scale_meters,
                distance_meters=distance_meters,
                focal_length_mm=estimated_focal,
                use_horizontal=False
            )
        
        if shot_type is None:
            for shot in self.CAMERA_SHOTS:
                dist_range = shot["distance_m"]
                if dist_range[0] <= distance_meters <= dist_range[1]:
                    shot_name = shot["name"]
                    if shot_name == "Extreme Close-Up":
                        shot_type = "extreme close-up"
                    elif shot_name == "Close-Up":
                        shot_type = "close-up"
                    elif shot_name == "Medium Close-Up":
                        shot_type = "medium close-up"
                    elif shot_name == "Medium Shot":
                        shot_type = "medium shot"
                    elif shot_name == "Medium Long Shot":
                        shot_type = "medium long shot"
                    elif shot_name == "Full Shot":
                        shot_type = "full shot"
                    elif shot_name == "Wide Shot":
                        shot_type = "wide shot"
                    elif shot_name == "Extreme Wide Shot":
                        shot_type = "extreme wide shot"
                    break
        
        if shot_type is None and fov is not None:
            try:
                fov_deg = float(fov)
                for shot in self.CAMERA_SHOTS:
                    fov_range = shot["fov_deg"]
                    if fov_range[0] <= fov_deg <= fov_range[1]:
                        shot_name = shot["name"]
                        if shot_name == "Extreme Close-Up":
                            shot_type = "extreme close-up"
                        elif shot_name == "Close-Up":
                            shot_type = "close-up"
                        elif shot_name == "Medium Close-Up":
                            shot_type = "medium close-up"
                        elif shot_name == "Medium Shot":
                            shot_type = "medium shot"
                        elif shot_name == "Medium Long Shot":
                            shot_type = "medium long shot"
                        elif shot_name == "Full Shot":
                            shot_type = "full shot"
                        elif shot_name == "Wide Shot":
                            shot_type = "wide shot"
                        elif shot_name == "Extreme Wide Shot":
                            shot_type = "extreme wide shot"
                        break
            except (ValueError, TypeError):
                pass
        
        if shot_type is None and estimated_focal is not None:
            for shot in self.CAMERA_SHOTS:
                focal_range = shot["focal_length_mm"]
                if focal_range[0] <= estimated_focal <= focal_range[1]:
                    shot_name = shot["name"]
                    if shot_name == "Extreme Close-Up":
                        shot_type = "extreme close-up"
                    elif shot_name == "Close-Up":
                        shot_type = "close-up"
                    elif shot_name == "Medium Close-Up":
                        shot_type = "medium close-up"
                    elif shot_name == "Medium Shot":
                        shot_type = "medium shot"
                    elif shot_name == "Medium Long Shot":
                        shot_type = "medium long shot"
                    elif shot_name == "Full Shot":
                        shot_type = "full shot"
                    elif shot_name == "Wide Shot":
                        shot_type = "wide shot"
                    elif shot_name == "Extreme Wide Shot":
                        shot_type = "extreme wide shot"
                    break
        
        if shot_type is None:
            if distance_meters < self.EXTREME_CLOSE_UP_MAX:
                shot_type = "extreme close-up"
            elif distance_meters < self.CLOSE_UP_MAX:
                shot_type = "close-up"
            elif distance_meters < self.MEDIUM_SHOT_MAX:
                shot_type = "medium shot"
            elif distance_meters < self.FULL_SHOT_MAX:
                shot_type = "full shot"
            elif distance_meters < self.WIDE_SHOT_MAX:
                shot_type = "wide shot"
            else:
                shot_type = "extreme wide shot"
        
        camera_info_parts = [f"camera distance {distance_str}"]
        
        focal_to_display = focal_length_mm if focal_length_mm is not None else estimated_focal
        if focal_to_display is not None:
            camera_info_parts.append(f"{int(focal_to_display)}mm")
        
        if fov is not None:
            fov_deg = int(fov) if isinstance(fov, (int, float)) else None
            if fov_deg:
                camera_info_parts.append(f"FOV {fov_deg}°")
        
        camera_info = " ".join(camera_info_parts)
        return f"{shot_type} ({camera_info})"
    
    def _get_camera_position_prompt(self, position, target, pitch, yaw):
        """Get camera position prompt"""
        if not position or not target:
            return ""
        
        def safe_float(value, default=0.0):
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        pos_x = safe_float(position.get("x", 0)) - safe_float(target.get("x", 0))
        pos_y = safe_float(position.get("y", 0)) - safe_float(target.get("y", 0))
        pos_z = safe_float(position.get("z", 0)) - safe_float(target.get("z", 0))
        
        horizontal_dist = math.sqrt(pos_x * pos_x + pos_z * pos_z)
        
        if horizontal_dist < 0.001:
            return "above object" if pos_y > 0 else "below object"
        
        angle_deg = math.degrees(math.atan2(pos_x, pos_z))
        if angle_deg < 0:
            angle_deg += 360
        
        parts = []
        angle_int = int(angle_deg)
        is_directly_front = (abs(angle_int) < 2 or abs(angle_int - 360) < 2) and pos_z > 0.1
        
        if is_directly_front:
            return ""
        
        if pos_z < -0.1:
            if abs(pos_x) < 0.1:
                parts.append("looking from behind")
            else:
                if 90 <= angle_int <= 180:
                    parts.append(f"Pan the camera {angle_int} degrees to the right-back side")
                elif 180 < angle_int <= 270:
                    parts.append(f"Pan the camera {angle_int} degrees to the left-back side")
                else:
                    parts.append(f"looking from behind at {angle_int} degree")
        else:
            if abs(pos_x) < 0.1:
                if pos_z > 0.1:
                    return ""
                else:
                    parts.append("looking from behind")
            else:
                if pos_x > 0.1:
                    parts.append(f"Pan the camera {angle_int} degrees to the right")
                elif pos_x < -0.1:
                    if angle_int >= 270:
                        left_angle = 360 - angle_int
                        parts.append(f"Pan the camera {left_angle} degrees to the left")
                    elif angle_int > 180:
                        left_angle = angle_int
                        parts.append(f"Pan the camera {left_angle} degrees to the left")
                    else:
                        parts.append(f"Pan the camera {angle_int} degrees to the left")
        
        return ", ".join(parts) if parts else ""


NODE_CLASS_MAPPINGS = {
    "AdvancedCameraControlNode": AdvancedCameraControlNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedCameraControlNode": "Advanced Camera Control Prompt Generator"
}
