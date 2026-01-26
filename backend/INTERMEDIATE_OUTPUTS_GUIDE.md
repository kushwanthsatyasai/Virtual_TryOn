# Intermediate Outputs Generator - Guide

This tool generates and saves intermediate outputs from each stage of the VTON preprocessing pipeline. It's useful for:
- Understanding the pipeline
- Debugging issues
- Visualizing each processing step
- Creating documentation/presentations
- Research paper figures

---

## Quick Start

### Option 1: Using the Batch File (Windows)

```cmd
cd backend
run_intermediate_outputs.bat
```

Then select:
- Option 1: Use test images (if available in `static/test_images/`)
- Option 2: Specify your own image paths

### Option 2: Command Line

```cmd
cd backend
venv_py311\Scripts\activate
python generate_intermediate_outputs.py --person "path/to/person.jpg"
```

With garment image:
```cmd
python generate_intermediate_outputs.py --person "path/to/person.jpg" --garment "path/to/garment.jpg"
```

---

## What Gets Generated

The script creates a timestamped folder `intermediate_outputs_YYYYMMDD_HHMMSS/` containing:

### 1. Original Images
- `01_original_person.jpg` - Input person image
- `01_original_garment.jpg` - Input garment image (if provided)

### 2. Color Processing
- `02a_L_channel.jpg` - Luminance channel (LAB)
- `02b_A_channel.jpg` - A channel (green-red)
- `02c_B_channel.jpg` - B channel (blue-yellow)

### 3. Enhancement
- `03a_L_enhanced.jpg` - CLAHE enhanced luminance
- `03b_person_enhanced.jpg` - Full enhanced image

### 4. Resizing
- `04_resized_with_padding.jpg` - Standardized 1024×768 with padding

### 5. Segmentation
- `05a_person_segmented_rgba.png` - Person with removed background
- `05b_segmentation_mask.jpg` - Binary segmentation mask
- `05c_mask_overlay.jpg` - Mask overlaid on original

### 6. Pose Detection
- `06_pose_landmarks.json` - 33 body landmarks with coordinates
- `06_pose_visualization.jpg` - Visual representation of detected pose
- `06_body_measurements.json` - Calculated measurements

### 7. Edge Detection
- `07_edges_canny.jpg` - Canny edge detection output

### 8. Sharpening
- `08_sharpened.jpg` - Unsharp mask applied

### 9. Noise Reduction
- `09_bilateral_filtered.jpg` - Bilateral filter applied

### 10. Comparison
- `10_comparison_grid.jpg` - 3×3 grid showing all stages

### 11. Metrics
- `11_quality_metrics.json` - Sharpness, brightness, contrast values

---

## Output Explanation

### Segmentation Mask
- **White pixels (255)**: Person/foreground
- **Black pixels (0)**: Background
- Used to isolate the person from the background

### Pose Landmarks
33 keypoints detected:
- **0**: Nose
- **11-12**: Left/Right Shoulder
- **13-14**: Left/Right Elbow
- **15-16**: Left/Right Wrist
- **23-24**: Left/Right Hip
- **25-26**: Left/Right Knee
- **27-28**: Left/Right Ankle

Each landmark has:
- `x, y`: Normalized coordinates [0, 1]
- `z`: Depth relative to hips
- `visibility`: Confidence score [0, 1]

### Body Measurements
- `shoulder_width`: Distance between shoulders (pixels)
- `torso_height`: Shoulder center to hip center (pixels)
- Used for garment sizing and warping

### Quality Metrics
- **Sharpness**: Laplacian variance (higher = sharper)
  - Good: > 100
  - Blurry: < 50
- **Brightness**: Mean luminance [0-255]
  - Good: 50-200
  - Too dark: < 50
  - Too bright: > 200
- **Contrast**: Standard deviation of luminance
  - Good: > 30
  - Low contrast: < 20

---

## Example Usage Scenarios

### 1. Check Image Quality Before VTON
```cmd
python generate_intermediate_outputs.py --person "my_photo.jpg"
```
Look at:
- Sharpness score in `11_quality_metrics.json`
- Segmentation quality in `05b_segmentation_mask.jpg`
- Pose detection in `06_pose_visualization.jpg`

### 2. Debug Segmentation Issues
If try-on results have background artifacts:
1. Generate intermediate outputs
2. Check `05b_segmentation_mask.jpg`
3. If mask is poor, try:
   - Better lighting in original photo
   - Simpler background
   - Higher resolution image

### 3. Debug Pose Issues
If garment doesn't align properly:
1. Check `06_pose_visualization.jpg`
2. Verify all key landmarks are detected
3. If shoulders/hips missing, try:
   - Full body or upper body shot
   - Frontal pose
   - Clear visibility of body parts

### 4. Create Presentation Figures
Use `10_comparison_grid.jpg` to show:
- Complete preprocessing pipeline
- Before/after comparisons
- Processing stages for papers/presentations

---

## Troubleshooting

### "Module not found" errors
Install required dependencies:
```cmd
pip install opencv-python pillow numpy matplotlib mediapipe rembg
```

### "No pose detected"
Possible causes:
- Person not clearly visible
- Extreme pose or angle
- Low resolution image
- Heavy occlusion

Solutions:
- Use frontal or semi-frontal pose
- Ensure person occupies >30% of image
- Use resolution >512×512
- Clear background

### Segmentation creates poor mask
Solutions:
- Use higher contrast between person and background
- Avoid busy/cluttered backgrounds
- Ensure good lighting
- Try different background removal settings

### Image too large / Out of memory
- Use smaller input images (<2048×2048)
- Close other applications
- Process one image at a time

---

## Integration with Research Paper

### For Methodology Section
Use these outputs to illustrate:
1. **Figure: Preprocessing Pipeline**
   - Use `10_comparison_grid.jpg`
   - Shows all 9 processing stages

2. **Figure: Segmentation Results**
   - Use `05c_mask_overlay.jpg`
   - Demonstrates segmentation accuracy

3. **Figure: Pose Detection**
   - Use `06_pose_visualization.jpg`
   - Shows 33 detected landmarks

4. **Table: Quality Metrics**
   - Extract from `11_quality_metrics.json`
   - Report sharpness, brightness, contrast

### For Results Section
- Compare metrics across different images
- Show success/failure cases
- Demonstrate robustness

---

## Advanced Usage

### Process Multiple Images
Create a batch script:

```python
import os
from generate_intermediate_outputs import generate_intermediate_outputs

person_images = ["person1.jpg", "person2.jpg", "person3.jpg"]

for img in person_images:
    print(f"\nProcessing {img}...")
    output_dir = generate_intermediate_outputs(img)
    print(f"Output: {output_dir}")
```

### Custom Processing
Modify `generate_intermediate_outputs.py` to:
- Add more stages
- Change parameters (CLAHE clip limit, etc.)
- Save additional formats
- Generate videos showing progression

---

## File Sizes

Typical output folder size: 10-50 MB
- Original images: 1-5 MB each
- Processed images: 1-3 MB each
- JSON files: <100 KB
- Comparison grid: 3-5 MB

---

## Tips for Best Results

### Input Image Requirements
- **Resolution**: 512×512 to 2048×2048
- **Format**: JPEG, PNG, WEBP
- **Person**: Clear, well-lit, frontal or semi-frontal
- **Background**: Simple, contrasting with person
- **Clothing**: Visible, not heavily occluded

### Recommended Poses
- ✅ Standing straight, arms at sides
- ✅ Standing with arms slightly away from body
- ✅ Upper body frontal view
- ❌ Sitting (lower body hidden)
- ❌ Extreme side view
- ❌ Arms crossed (occludes torso)

### Lighting
- Even, diffused lighting preferred
- Avoid harsh shadows
- Avoid backlighting
- Natural or studio lighting works best

---

## Next Steps

After reviewing intermediate outputs:

1. **If quality is good**:
   - Proceed with full VTON generation
   - Use the processed person image

2. **If quality issues found**:
   - Retake photo with better conditions
   - Try different preprocessing parameters
   - Manual editing if needed

3. **For research**:
   - Document the pipeline
   - Report quality metrics
   - Use visualizations in paper

---

## Support

If you encounter issues:
1. Check error messages in console
2. Verify input image paths
3. Ensure all dependencies installed
4. Check image meets requirements
5. Review quality metrics JSON

---

## Example Output Structure

```
intermediate_outputs_20260119_143025/
├── 01_original_person.jpg
├── 02a_L_channel.jpg
├── 02b_A_channel.jpg
├── 02c_B_channel.jpg
├── 03a_L_enhanced.jpg
├── 03b_person_enhanced.jpg
├── 04_resized_with_padding.jpg
├── 05a_person_segmented_rgba.png
├── 05b_segmentation_mask.jpg
├── 05c_mask_overlay.jpg
├── 06_pose_landmarks.json
├── 06_pose_visualization.jpg
├── 06_body_measurements.json
├── 07_edges_canny.jpg
├── 08_sharpened.jpg
├── 09_bilateral_filtered.jpg
├── 10_comparison_grid.jpg
└── 11_quality_metrics.json
```

---

**Generated**: January 2026  
**Version**: 1.0
