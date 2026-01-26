"""
Generate Intermediate Outputs from VTON Pipeline
This script saves outputs from each stage of preprocessing and VTON
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime

# Add app to path
sys.path.append(os.path.dirname(__file__))

def create_output_dir():
    """Create directory for intermediate outputs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"intermediate_outputs_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def save_image(image, filename, output_dir):
    """Save image to output directory"""
    filepath = os.path.join(output_dir, filename)
    if isinstance(image, np.ndarray):
        if len(image.shape) == 2:  # Grayscale
            cv2.imwrite(filepath, image)
        else:  # RGB
            cv2.imwrite(filepath, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    else:  # PIL Image
        image.save(filepath)
    print(f"Saved: {filename}")

def visualize_pose(image, landmarks, output_dir, filename="06_pose_visualization.jpg"):
    """Visualize pose landmarks on image"""
    import mediapipe as mp
    
    vis_image = image.copy()
    h, w = vis_image.shape[:2]
    
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    # Draw landmarks
    for idx, lm in enumerate(landmarks):
        x = int(lm['x'] * w)
        y = int(lm['y'] * h)
        
        # Draw point
        cv2.circle(vis_image, (x, y), 5, (0, 255, 0), -1)
        
        # Draw landmark number
        cv2.putText(vis_image, str(idx), (x+5, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    # Draw connections
    connections = [
        (11, 12),  # Shoulders
        (11, 13), (13, 15),  # Left arm
        (12, 14), (14, 16),  # Right arm
        (11, 23), (12, 24),  # Torso
        (23, 24),  # Hips
        (23, 25), (25, 27),  # Left leg
        (24, 26), (26, 28),  # Right leg
    ]
    
    for connection in connections:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            
            x1, y1 = int(start['x'] * w), int(start['y'] * h)
            x2, y2 = int(end['x'] * w), int(end['y'] * h)
            
            cv2.line(vis_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    save_image(vis_image, filename, output_dir)
    return vis_image

def generate_intermediate_outputs(person_image_path, garment_image_path=None):
    """
    Generate and save intermediate outputs from VTON pipeline
    """
    print("="*60)
    print("GENERATING INTERMEDIATE OUTPUTS FROM VTON PIPELINE")
    print("="*60)
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"\nOutput directory: {output_dir}\n")
    
    # ============================================================
    # STAGE 1: Load Original Images
    # ============================================================
    print("\n[STAGE 1] Loading original images...")
    
    person_img = Image.open(person_image_path).convert('RGB')
    person_np = np.array(person_img)
    
    save_image(person_img, "01_original_person.jpg", output_dir)
    
    if garment_image_path:
        garment_img = Image.open(garment_image_path).convert('RGB')
        garment_np = np.array(garment_img)
        save_image(garment_img, "01_original_garment.jpg", output_dir)
    
    # ============================================================
    # STAGE 2: Preprocessing - Color Normalization
    # ============================================================
    print("\n[STAGE 2] Color normalization...")
    
    # Convert to LAB for white balance
    person_bgr = cv2.cvtColor(person_np, cv2.COLOR_RGB2BGR)
    person_lab = cv2.cvtColor(person_bgr, cv2.COLOR_BGR2LAB)
    
    # Save LAB channels separately
    l_channel, a_channel, b_channel = cv2.split(person_lab)
    save_image(l_channel, "02a_L_channel.jpg", output_dir)
    save_image(a_channel, "02b_A_channel.jpg", output_dir)
    save_image(b_channel, "02c_B_channel.jpg", output_dir)
    
    # ============================================================
    # STAGE 3: CLAHE Enhancement
    # ============================================================
    print("\n[STAGE 3] CLAHE contrast enhancement...")
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    
    save_image(l_enhanced, "03a_L_enhanced.jpg", output_dir)
    
    # Merge back
    lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
    person_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
    save_image(person_enhanced, "03b_person_enhanced.jpg", output_dir)
    
    # ============================================================
    # STAGE 4: Resolution Standardization
    # ============================================================
    print("\n[STAGE 4] Resolution standardization...")
    
    target_size = (1024, 768)
    h, w = person_enhanced.shape[:2]
    scale = min(target_size[0] / w, target_size[1] / h)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    person_resized = cv2.resize(person_enhanced, (new_w, new_h), 
                                interpolation=cv2.INTER_LANCZOS4)
    
    # Create canvas with padding
    canvas = np.ones((target_size[1], target_size[0], 3), dtype=np.uint8) * 255
    pad_w = (target_size[0] - new_w) // 2
    pad_h = (target_size[1] - new_h) // 2
    canvas[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = person_resized
    
    save_image(canvas, "04_resized_with_padding.jpg", output_dir)
    
    # ============================================================
    # STAGE 5: Semantic Segmentation (U2-Net)
    # ============================================================
    print("\n[STAGE 5] Semantic segmentation (this may take a moment)...")
    
    try:
        from rembg import remove
        
        # Remove background
        person_pil = Image.fromarray(canvas)
        person_no_bg = remove(person_pil)
        
        # Save image with alpha channel
        save_image(person_no_bg, "05a_person_segmented_rgba.png", output_dir)
        
        # Extract and save mask
        person_no_bg_np = np.array(person_no_bg)
        if person_no_bg_np.shape[2] == 4:
            mask = person_no_bg_np[:, :, 3]
        else:
            # Fallback: create mask from non-white pixels
            gray = cv2.cvtColor(canvas, cv2.COLOR_RGB2GRAY)
            _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        
        save_image(mask, "05b_segmentation_mask.jpg", output_dir)
        
        # Save mask overlay
        mask_colored = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
        mask_colored_rgb = cv2.cvtColor(mask_colored, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(canvas, 0.6, mask_colored_rgb, 0.4, 0)
        save_image(overlay, "05c_mask_overlay.jpg", output_dir)
        
    except Exception as e:
        print(f"Segmentation failed: {e}")
        print("Creating simple threshold mask...")
        gray = cv2.cvtColor(canvas, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        save_image(mask, "05b_segmentation_mask.jpg", output_dir)
    
    # ============================================================
    # STAGE 6: Pose Estimation
    # ============================================================
    print("\n[STAGE 6] Pose estimation...")
    
    try:
        import mediapipe as mp
        
        mp_holistic = mp.solutions.holistic.Holistic(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            refine_face_landmarks=False
        )
        
        # Process image
        results = mp_holistic.process(canvas)
        
        if results.pose_landmarks:
            # Extract landmarks
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': lm.x,
                    'y': lm.y,
                    'z': lm.z,
                    'visibility': lm.visibility
                })
            
            # Save landmarks data
            import json
            landmarks_file = os.path.join(output_dir, "06_pose_landmarks.json")
            with open(landmarks_file, 'w') as f:
                json.dump(landmarks, f, indent=2)
            print(f"Saved: 06_pose_landmarks.json ({len(landmarks)} landmarks)")
            
            # Visualize pose
            visualize_pose(canvas, landmarks, output_dir)
            
            # Calculate body measurements
            h, w = canvas.shape[:2]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            shoulder_width = np.sqrt(
                ((left_shoulder['x'] - right_shoulder['x']) * w)**2 +
                ((left_shoulder['y'] - right_shoulder['y']) * h)**2
            )
            
            shoulder_center_y = (left_shoulder['y'] + right_shoulder['y']) / 2
            hip_center_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            torso_height = abs(shoulder_center_y - hip_center_y) * h
            
            measurements = {
                'shoulder_width': float(shoulder_width),
                'torso_height': float(torso_height),
                'image_width': w,
                'image_height': h
            }
            
            measurements_file = os.path.join(output_dir, "06_body_measurements.json")
            with open(measurements_file, 'w') as f:
                json.dump(measurements, f, indent=2)
            print(f"Saved: 06_body_measurements.json")
            
        else:
            print("No pose detected in image")
            
    except Exception as e:
        print(f"Pose estimation failed: {e}")
    
    # ============================================================
    # STAGE 7: Edge Detection
    # ============================================================
    print("\n[STAGE 7] Edge detection...")
    
    gray = cv2.cvtColor(canvas, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    save_image(edges, "07_edges_canny.jpg", output_dir)
    
    # ============================================================
    # STAGE 8: Sharpening
    # ============================================================
    print("\n[STAGE 8] Unsharp masking...")
    
    gaussian = cv2.GaussianBlur(canvas, (0, 0), 1.0)
    sharpened = cv2.addWeighted(canvas, 1.5, gaussian, -0.5, 0)
    save_image(sharpened, "08_sharpened.jpg", output_dir)
    
    # ============================================================
    # STAGE 9: Noise Reduction (Bilateral Filter)
    # ============================================================
    print("\n[STAGE 9] Bilateral filtering...")
    
    bilateral = cv2.bilateralFilter(canvas, 9, 75, 75)
    save_image(bilateral, "09_bilateral_filtered.jpg", output_dir)
    
    # ============================================================
    # STAGE 10: Create Comparison Grid
    # ============================================================
    print("\n[STAGE 10] Creating comparison grid...")
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    fig.suptitle('VTON Pipeline - Intermediate Outputs', fontsize=16)
    
    images_to_compare = [
        (person_np, "1. Original Person"),
        (person_enhanced, "2. CLAHE Enhanced"),
        (canvas, "3. Resized + Padded"),
        (mask, "4. Segmentation Mask"),
        (overlay, "5. Mask Overlay"),
        (canvas, "6. Pose Detection"),
        (edges, "7. Edge Detection"),
        (sharpened, "8. Sharpened"),
        (bilateral, "9. Bilateral Filtered")
    ]
    
    for idx, (img, title) in enumerate(images_to_compare):
        ax = axes[idx // 3, idx % 3]
        if len(img.shape) == 2:  # Grayscale
            ax.imshow(img, cmap='gray')
        else:
            ax.imshow(img)
        ax.set_title(title)
        ax.axis('off')
    
    plt.tight_layout()
    comparison_path = os.path.join(output_dir, "10_comparison_grid.jpg")
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: 10_comparison_grid.jpg")
    
    # ============================================================
    # STAGE 11: Quality Metrics
    # ============================================================
    print("\n[STAGE 11] Calculating quality metrics...")
    
    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()
    
    # Brightness
    brightness = np.mean(l_channel)
    
    # Contrast
    contrast = np.std(l_channel)
    
    metrics = {
        'sharpness': float(sharpness),
        'brightness': float(brightness),
        'contrast': float(contrast),
        'image_size': canvas.shape[:2],
    }
    
    metrics_file = os.path.join(output_dir, "11_quality_metrics.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved: 11_quality_metrics.json")
    
    print(f"\nSharpness: {sharpness:.2f}")
    print(f"Brightness: {brightness:.2f}")
    print(f"Contrast: {contrast:.2f}")
    
    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "="*60)
    print("INTERMEDIATE OUTPUTS GENERATION COMPLETE!")
    print("="*60)
    print(f"\nAll outputs saved to: {output_dir}")
    print("\nGenerated files:")
    for filename in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, filename)
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        print(f"  - {filename} ({size_mb:.2f} MB)")
    
    return output_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate intermediate outputs from VTON pipeline')
    parser.add_argument('--person', type=str, required=True, 
                       help='Path to person image')
    parser.add_argument('--garment', type=str, default=None,
                       help='Path to garment image (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.person):
        print(f"Error: Person image not found: {args.person}")
        sys.exit(1)
    
    if args.garment and not os.path.exists(args.garment):
        print(f"Error: Garment image not found: {args.garment}")
        sys.exit(1)
    
    output_dir = generate_intermediate_outputs(args.person, args.garment)
    print(f"\nTo view the results, open the folder: {output_dir}")
