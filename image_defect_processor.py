# image_defect_processor.py
# Advanced image processing for defect detection in building survey photos

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import base64
import io
import json
from datetime import datetime
import os

class ImageDefectProcessor:
    def __init__(self):
        self.crack_detector = CrackDetector()
        self.moisture_detector = MoistureDetector()
        self.corrosion_detector = CorrosionDetector()
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def process_image(self, image_path_or_bytes, image_name="unknown"):
        """
        Main function to process building survey images for defects
        """
        try:
            # Load image
            if isinstance(image_path_or_bytes, str):
                image = cv2.imread(image_path_or_bytes)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                # Handle bytes data
                image_array = np.frombuffer(image_path_or_bytes, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if image is None:
                return {"error": "Could not load image"}
            
            # Initialize results
            results = {
                "image_name": image_name,
                "timestamp": datetime.now().isoformat(),
                "image_dimensions": {
                    "width": image.shape[1],
                    "height": image.shape[0]
                },
                "defects_detected": [],
                "confidence_scores": {},
                "processed_regions": []
            }
            
            # Detect various types of defects
            crack_results = self.crack_detector.detect_cracks(image)
            moisture_results = self.moisture_detector.detect_moisture(image_rgb)
            corrosion_results = self.corrosion_detector.detect_corrosion(image_rgb)
            
            # Compile results
            results["defects_detected"].extend(crack_results["defects"])
            results["defects_detected"].extend(moisture_results["defects"])
            results["defects_detected"].extend(corrosion_results["defects"])
            
            # Calculate overall confidence
            all_confidences = []
            all_confidences.extend(crack_results["confidences"])
            all_confidences.extend(moisture_results["confidences"])
            all_confidences.extend(corrosion_results["confidences"])
            
            if all_confidences:
                results["confidence_scores"]["overall"] = np.mean(all_confidences)
                results["confidence_scores"]["max"] = np.max(all_confidences)
                results["confidence_scores"]["min"] = np.min(all_confidences)
            
            # Generate annotated image
            annotated_image = self.create_annotated_image(image_rgb, results["defects_detected"])
            results["annotated_image_base64"] = self.image_to_base64(annotated_image)
            
            return results
            
        except Exception as e:
            return {"error": f"Image processing failed: {str(e)}"}
    
    def create_annotated_image(self, image, defects):
        """
        Create an annotated version of the image with defect highlights
        """
        annotated = image.copy()
        
        # Color mapping for different defect types
        colors = {
            "crack": (255, 0, 0),      # Red
            "moisture": (0, 0, 255),   # Blue
            "corrosion": (255, 165, 0), # Orange
            "mold": (128, 0, 128),     # Purple
            "structural": (255, 255, 0) # Yellow
        }
        
        for defect in defects:
            color = colors.get(defect["type"], (0, 255, 0))  # Default green
            
            if "bbox" in defect:
                # Draw bounding box
                x, y, w, h = defect["bbox"]
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                
                # Add label
                label = f"{defect['type']}: {defect['confidence']:.2f}"
                cv2.putText(annotated, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            elif "contour" in defect:
                # Draw contour
                cv2.drawContours(annotated, [defect["contour"]], -1, color, 2)
        
        return annotated
    
    def image_to_base64(self, image):
        """
        Convert image array to base64 string for web display
        """
        pil_image = Image.fromarray(image)
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"


class CrackDetector:
    def __init__(self):
        self.min_crack_length = 20
        self.max_line_gap = 10
    
    def detect_cracks(self, image):
        """
        Detect cracks using edge detection and line detection
        """
        results = {"defects": [], "confidences": []}
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
            
            # Detect lines using HoughLinesP
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                                   minLineLength=self.min_crack_length,
                                   maxLineGap=self.max_line_gap)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    
                    # Calculate confidence based on line properties
                    confidence = min(0.95, length / 100.0)
                    
                    if confidence > 0.3:  # Minimum confidence threshold
                        defect = {
                            "type": "crack",
                            "confidence": confidence,
                            "bbox": [min(x1, x2), min(y1, y2), 
                                    abs(x2-x1), abs(y2-y1)],
                            "length_pixels": length,
                            "coordinates": [[x1, y1], [x2, y2]]
                        }
                        results["defects"].append(defect)
                        results["confidences"].append(confidence)
            
        except Exception as e:
            print(f"Crack detection error: {e}")
        
        return results


class MoistureDetector:
    def __init__(self):
        # HSV ranges for moisture/water damage detection
        self.moisture_hsv_ranges = [
            # Dark stains
            (np.array([0, 0, 0]), np.array([180, 255, 100])),
            # Greenish mold
            (np.array([40, 50, 50]), np.array([80, 255, 255])),
            # Yellowish stains
            (np.array([20, 100, 100]), np.array([30, 255, 255]))
        ]
    
    def detect_moisture(self, image_rgb):
        """
        Detect moisture damage and stains using color analysis
        """
        results = {"defects": [], "confidences": []}
        
        try:
            # Convert RGB to HSV
            hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            
            for i, (lower, upper) in enumerate(self.moisture_hsv_ranges):
                # Create mask for this color range
                mask = cv2.inRange(hsv, lower, upper)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                              cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    
                    if area > 500:  # Minimum area threshold
                        # Calculate confidence based on area and shape
                        confidence = min(0.9, area / 10000.0)
                        
                        if confidence > 0.2:
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            defect = {
                                "type": "moisture",
                                "confidence": confidence,
                                "bbox": [x, y, w, h],
                                "area_pixels": area,
                                "contour": contour.tolist()
                            }
                            results["defects"].append(defect)
                            results["confidences"].append(confidence)
            
        except Exception as e:
            print(f"Moisture detection error: {e}")
        
        return results


class CorrosionDetector:
    def __init__(self):
        # HSV ranges for rust/corrosion detection
        self.rust_hsv_ranges = [
            # Reddish-brown rust
            (np.array([0, 50, 50]), np.array([20, 255, 255])),
            # Orange rust
            (np.array([5, 100, 100]), np.array([15, 255, 255]))
        ]
    
    def detect_corrosion(self, image_rgb):
        """
        Detect corrosion and rust using color analysis
        """
        results = {"defects": [], "confidences": []}
        
        try:
            # Convert RGB to HSV
            hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            
            for i, (lower, upper) in enumerate(self.rust_hsv_ranges):
                # Create mask for rust colors
                mask = cv2.inRange(hsv, lower, upper)
                
                # Apply morphological operations to clean up the mask
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                              cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    
                    if area > 300:  # Minimum area threshold
                        # Calculate confidence
                        confidence = min(0.85, area / 8000.0)
                        
                        if confidence > 0.25:
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            defect = {
                                "type": "corrosion",
                                "confidence": confidence,
                                "bbox": [x, y, w, h],
                                "area_pixels": area,
                                "contour": contour.tolist()
                            }
                            results["defects"].append(defect)
                            results["confidences"].append(confidence)
            
        except Exception as e:
            print(f"Corrosion detection error: {e}")
        
        return results


def process_survey_images(image_folder_path):
    """
    Process all images in a survey folder
    """
    processor = ImageDefectProcessor()
    results = []
    
    if not os.path.exists(image_folder_path):
        return {"error": "Image folder not found"}
    
    for filename in os.listdir(image_folder_path):
        file_path = os.path.join(image_folder_path, filename)
        
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in processor.supported_formats:
                result = processor.process_image(file_path, filename)
                results.append(result)
    
    return {
        "total_images": len(results),
        "images_with_defects": len([r for r in results if r.get("defects_detected", [])]),
        "results": results
    }


# Usage example
if __name__ == "__main__":
    processor = ImageDefectProcessor()
    
    # Example usage
    sample_result = processor.process_image("sample_building_image.jpg")
    print(json.dumps(sample_result, indent=2, default=str))
