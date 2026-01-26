"""
Advanced Quality Evaluation Metrics for Virtual Try-On
======================================================
Calculates comprehensive metrics for research paper evaluation:
- Image Quality Metrics (PSNR, SSIM, MSE)
- Perceptual Metrics (LPIPS - Learned Perceptual Image Patch Similarity)
- Structural Metrics (Edge preservation, Pose consistency)
- Color Metrics (Color distribution similarity)
- Feature-based Metrics (Deep feature similarity)
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime
from typing import Dict, Tuple, Optional
from pathlib import Path

# Image quality metrics
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import mean_squared_error as mse

# Try to import advanced metrics
try:
    import torch
    import torchvision.models as models
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except:
    TORCH_AVAILABLE = False
    print("PyTorch not available - some metrics will be skipped")

try:
    import lpips
    LPIPS_AVAILABLE = True
except:
    LPIPS_AVAILABLE = False
    print("LPIPS not available - perceptual metric will be skipped")


class VirtualTryOnEvaluator:
    """
    Comprehensive evaluation suite for virtual try-on quality assessment.
    """
    
    def __init__(self):
        """Initialize evaluator with metric models"""
        
        # LPIPS for perceptual similarity (if available)
        self.lpips_model = None
        if LPIPS_AVAILABLE and TORCH_AVAILABLE:
            try:
                self.lpips_model = lpips.LPIPS(net='alex')  # or 'vgg', 'squeeze'
                self.lpips_model.eval()
                print("[OK] LPIPS perceptual metric loaded")
            except:
                print("[SKIP] LPIPS failed to load")
        
        # Feature extractor for deep similarity
        self.feature_extractor = None
        if TORCH_AVAILABLE:
            try:
                resnet = models.resnet50(pretrained=True)
                self.feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
                self.feature_extractor.eval()
                print("[OK] ResNet feature extractor loaded")
            except:
                print("[SKIP] ResNet failed to load")
        
        self.transform = None
        if TORCH_AVAILABLE:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
    
    def evaluate_tryon(
        self,
        generated_image_path: str,
        reference_person_path: str,
        reference_cloth_path: str,
        output_json_path: Optional[str] = None
    ) -> Dict:
        """
        Evaluate a virtual try-on result comprehensively.
        
        Args:
            generated_image_path: Path to generated try-on result
            reference_person_path: Path to original person image
            reference_cloth_path: Path to original garment image
            output_json_path: Optional path to save metrics JSON
            
        Returns:
            Dictionary containing all computed metrics
        """
        print("\n" + "="*70)
        print("VIRTUAL TRY-ON QUALITY EVALUATION")
        print("="*70)
        
        # Load images
        generated = cv2.imread(generated_image_path)
        person = cv2.imread(reference_person_path)
        cloth = cv2.imread(reference_cloth_path)
        
        if generated is None or person is None or cloth is None:
            raise ValueError("Failed to load one or more images")
        
        # Ensure same size for comparison
        h, w = generated.shape[:2]
        person_resized = cv2.resize(person, (w, h))
        cloth_resized = cv2.resize(cloth, (w, h))
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'image_paths': {
                'generated': generated_image_path,
                'person': reference_person_path,
                'cloth': reference_cloth_path
            },
            'image_dimensions': {'width': w, 'height': h}
        }
        
        # === 1. BASIC IMAGE QUALITY METRICS ===
        print("\n[1/9] Computing basic image quality metrics...")
        metrics['basic_quality'] = self._compute_basic_quality(generated)
        
        # === 2. STRUCTURAL SIMILARITY (SSIM) ===
        print("[2/9] Computing structural similarity (SSIM)...")
        metrics['ssim'] = self._compute_ssim(generated, person_resized)
        
        # === 3. PEAK SIGNAL-TO-NOISE RATIO (PSNR) ===
        print("[3/9] Computing PSNR...")
        metrics['psnr'] = self._compute_psnr(generated, person_resized)
        
        # === 4. PERCEPTUAL SIMILARITY (LPIPS) ===
        print("[4/9] Computing perceptual similarity (LPIPS)...")
        metrics['lpips'] = self._compute_lpips(
            generated_image_path,
            reference_person_path
        )
        
        # === 5. COLOR DISTRIBUTION METRICS ===
        print("[5/9] Computing color distribution metrics...")
        metrics['color_metrics'] = self._compute_color_metrics(
            generated,
            person_resized,
            cloth_resized
        )
        
        # === 6. EDGE PRESERVATION ===
        print("[6/9] Computing edge preservation metrics...")
        metrics['edge_preservation'] = self._compute_edge_preservation(
            generated,
            person_resized
        )
        
        # === 7. TEXTURE METRICS ===
        print("[7/9] Computing texture quality metrics...")
        metrics['texture_quality'] = self._compute_texture_metrics(generated)
        
        # === 8. DEEP FEATURE SIMILARITY ===
        print("[8/9] Computing deep feature similarity...")
        metrics['feature_similarity'] = self._compute_feature_similarity(
            generated_image_path,
            reference_person_path
        )
        
        # === 9. COMPOSITE SCORE ===
        print("[9/9] Computing composite quality score...")
        metrics['composite_score'] = self._compute_composite_score(metrics)
        
        # Save to JSON if requested
        if output_json_path:
            os.makedirs(os.path.dirname(output_json_path) or '.', exist_ok=True)
            with open(output_json_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\n[SAVED] Metrics saved to: {output_json_path}")
        
        # Print summary
        self._print_summary(metrics)
        
        return metrics
    
    def _compute_basic_quality(self, image: np.ndarray) -> Dict:
        """Compute basic image quality metrics"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var())
        
        # Brightness
        brightness = float(np.mean(gray))
        
        # Contrast
        contrast = float(np.std(gray))
        
        # Dynamic range
        dynamic_range = float(np.max(gray) - np.min(gray))
        
        return {
            'sharpness': sharpness,
            'brightness': brightness,
            'contrast': contrast,
            'dynamic_range': dynamic_range
        }
    
    def _compute_ssim(self, img1: np.ndarray, img2: np.ndarray) -> Dict:
        """Compute Structural Similarity Index (SSIM)"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Compute SSIM
        ssim_score, ssim_map = ssim(gray1, gray2, full=True, data_range=255)
        
        # SSIM per channel
        ssim_r = ssim(img1[:,:,0], img2[:,:,0], data_range=255)
        ssim_g = ssim(img1[:,:,1], img2[:,:,1], data_range=255)
        ssim_b = ssim(img1[:,:,2], img2[:,:,2], data_range=255)
        
        return {
            'overall': float(ssim_score),
            'per_channel': {
                'r': float(ssim_r),
                'g': float(ssim_g),
                'b': float(ssim_b)
            },
            'interpretation': self._interpret_ssim(ssim_score)
        }
    
    def _interpret_ssim(self, ssim_value: float) -> str:
        """Interpret SSIM value"""
        if ssim_value > 0.9:
            return "Excellent (>0.9)"
        elif ssim_value > 0.8:
            return "Good (0.8-0.9)"
        elif ssim_value > 0.7:
            return "Fair (0.7-0.8)"
        elif ssim_value > 0.5:
            return "Poor (0.5-0.7)"
        else:
            return "Very Poor (<0.5)"
    
    def _compute_psnr(self, img1: np.ndarray, img2: np.ndarray) -> Dict:
        """Compute Peak Signal-to-Noise Ratio (PSNR)"""
        # PSNR overall
        psnr_score = psnr(img1, img2, data_range=255)
        
        # MSE (Mean Squared Error)
        mse_score = mse(img1, img2)
        
        return {
            'psnr_db': float(psnr_score),
            'mse': float(mse_score),
            'interpretation': self._interpret_psnr(psnr_score)
        }
    
    def _interpret_psnr(self, psnr_value: float) -> str:
        """Interpret PSNR value"""
        if psnr_value > 40:
            return "Excellent (>40 dB)"
        elif psnr_value > 30:
            return "Good (30-40 dB)"
        elif psnr_value > 20:
            return "Fair (20-30 dB)"
        else:
            return "Poor (<20 dB)"
    
    def _compute_lpips(self, img1_path: str, img2_path: str) -> Dict:
        """Compute Learned Perceptual Image Patch Similarity (LPIPS)"""
        if not LPIPS_AVAILABLE or not TORCH_AVAILABLE or self.lpips_model is None:
            return {
                'score': None,
                'available': False,
                'note': 'LPIPS not available (install: pip install lpips)'
            }
        
        try:
            # Load images
            img1 = lpips.im2tensor(lpips.load_image(img1_path))
            img2 = lpips.im2tensor(lpips.load_image(img2_path))
            
            # Compute LPIPS (lower is better, 0 = identical)
            with torch.no_grad():
                lpips_score = self.lpips_model(img1, img2).item()
            
            return {
                'score': float(lpips_score),
                'available': True,
                'interpretation': self._interpret_lpips(lpips_score)
            }
        except Exception as e:
            return {
                'score': None,
                'available': False,
                'error': str(e)
            }
    
    def _interpret_lpips(self, lpips_value: float) -> str:
        """Interpret LPIPS value (lower is better)"""
        if lpips_value < 0.1:
            return "Excellent (<0.1)"
        elif lpips_value < 0.2:
            return "Good (0.1-0.2)"
        elif lpips_value < 0.3:
            return "Fair (0.2-0.3)"
        else:
            return "Poor (>0.3)"
    
    def _compute_color_metrics(
        self,
        generated: np.ndarray,
        person: np.ndarray,
        cloth: np.ndarray
    ) -> Dict:
        """Compute color distribution and preservation metrics"""
        
        # Convert to different color spaces
        gen_hsv = cv2.cvtColor(generated, cv2.COLOR_BGR2HSV)
        gen_lab = cv2.cvtColor(generated, cv2.COLOR_BGR2LAB)
        cloth_hsv = cv2.cvtColor(cloth, cv2.COLOR_BGR2HSV)
        cloth_lab = cv2.cvtColor(cloth, cv2.COLOR_BGR2LAB)
        
        # Color histogram comparison
        hist_gen = cv2.calcHist([generated], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist_cloth = cv2.calcHist([cloth], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        hist_gen = cv2.normalize(hist_gen, hist_gen).flatten()
        hist_cloth = cv2.normalize(hist_cloth, hist_cloth).flatten()
        
        # Histogram correlation
        color_correlation = float(cv2.compareHist(
            hist_gen.reshape(-1, 1),
            hist_cloth.reshape(-1, 1),
            cv2.HISTCMP_CORREL
        ))
        
        # Mean color difference (LAB space - perceptually uniform)
        color_diff_lab = np.mean(np.abs(gen_lab.astype(float) - cloth_lab.astype(float)))
        
        # Saturation metrics
        gen_saturation = np.mean(gen_hsv[:, :, 1])
        cloth_saturation = np.mean(cloth_hsv[:, :, 1])
        saturation_preservation = 1.0 - abs(gen_saturation - cloth_saturation) / 255.0
        
        return {
            'color_correlation': color_correlation,
            'color_difference_lab': float(color_diff_lab),
            'saturation_preservation': float(saturation_preservation),
            'mean_saturation_generated': float(gen_saturation),
            'mean_saturation_cloth': float(cloth_saturation)
        }
    
    def _compute_edge_preservation(
        self,
        generated: np.ndarray,
        reference: np.ndarray
    ) -> Dict:
        """Compute edge preservation metrics"""
        
        # Convert to grayscale
        gen_gray = cv2.cvtColor(generated, cv2.COLOR_BGR2GRAY)
        ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        
        # Compute edges
        gen_edges = cv2.Canny(gen_gray, 50, 150)
        ref_edges = cv2.Canny(ref_gray, 50, 150)
        
        # Edge density
        gen_edge_density = np.sum(gen_edges > 0) / gen_edges.size
        ref_edge_density = np.sum(ref_edges > 0) / ref_edges.size
        
        # Edge preservation ratio
        edge_preservation = min(gen_edge_density, ref_edge_density) / max(gen_edge_density, ref_edge_density)
        
        # Edge agreement (intersection over union)
        edge_intersection = np.sum((gen_edges > 0) & (ref_edges > 0))
        edge_union = np.sum((gen_edges > 0) | (ref_edges > 0))
        edge_iou = edge_intersection / edge_union if edge_union > 0 else 0
        
        return {
            'edge_preservation_ratio': float(edge_preservation),
            'edge_iou': float(edge_iou),
            'generated_edge_density': float(gen_edge_density),
            'reference_edge_density': float(ref_edge_density)
        }
    
    def _compute_texture_metrics(self, image: np.ndarray) -> Dict:
        """Compute texture quality metrics"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Local variance (texture richness)
        kernel_size = 7
        mean_filtered = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
        sqr_filtered = cv2.blur((gray.astype(float))**2, (kernel_size, kernel_size))
        local_variance = sqr_filtered - mean_filtered**2
        texture_richness = float(np.mean(local_variance))
        
        # Entropy (information content)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist / hist.sum()
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        # Gradient magnitude (detail level)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        detail_level = float(np.mean(gradient_magnitude))
        
        return {
            'texture_richness': texture_richness,
            'entropy': float(entropy),
            'detail_level': detail_level
        }
    
    def _compute_feature_similarity(self, img1_path: str, img2_path: str) -> Dict:
        """Compute deep feature similarity using ResNet"""
        if not TORCH_AVAILABLE or self.feature_extractor is None:
            return {
                'cosine_similarity': None,
                'available': False,
                'note': 'Deep features require PyTorch'
            }
        
        try:
            # Load and preprocess images
            img1 = Image.open(img1_path).convert('RGB')
            img2 = Image.open(img2_path).convert('RGB')
            
            tensor1 = self.transform(img1).unsqueeze(0)
            tensor2 = self.transform(img2).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                feat1 = self.feature_extractor(tensor1).flatten().numpy()
                feat2 = self.feature_extractor(tensor2).flatten().numpy()
            
            # Normalize
            feat1 = feat1 / np.linalg.norm(feat1)
            feat2 = feat2 / np.linalg.norm(feat2)
            
            # Cosine similarity
            cosine_sim = float(np.dot(feat1, feat2))
            
            return {
                'cosine_similarity': cosine_sim,
                'available': True,
                'interpretation': self._interpret_cosine_sim(cosine_sim)
            }
        except Exception as e:
            return {
                'cosine_similarity': None,
                'available': False,
                'error': str(e)
            }
    
    def _interpret_cosine_sim(self, sim: float) -> str:
        """Interpret cosine similarity"""
        if sim > 0.9:
            return "Very Similar (>0.9)"
        elif sim > 0.8:
            return "Similar (0.8-0.9)"
        elif sim > 0.7:
            return "Moderately Similar (0.7-0.8)"
        else:
            return "Different (<0.7)"
    
    def _compute_composite_score(self, metrics: Dict) -> Dict:
        """
        Compute a composite quality score (0-100)
        Weighted combination of multiple metrics
        """
        scores = []
        weights = []
        
        # SSIM (weight: 0.25)
        if metrics['ssim']['overall'] is not None:
            scores.append(metrics['ssim']['overall'] * 100)
            weights.append(0.25)
        
        # Sharpness (normalized, weight: 0.15)
        sharpness = metrics['basic_quality']['sharpness']
        sharpness_score = min(sharpness / 1000.0 * 100, 100)
        scores.append(sharpness_score)
        weights.append(0.15)
        
        # Color preservation (weight: 0.20)
        color_corr = metrics['color_metrics']['color_correlation']
        scores.append(color_corr * 100)
        weights.append(0.20)
        
        # Edge preservation (weight: 0.15)
        edge_iou = metrics['edge_preservation']['edge_iou']
        scores.append(edge_iou * 100)
        weights.append(0.15)
        
        # Texture quality (normalized, weight: 0.10)
        entropy = metrics['texture_quality']['entropy']
        texture_score = min(entropy / 8.0 * 100, 100)
        scores.append(texture_score)
        weights.append(0.10)
        
        # Deep feature similarity (weight: 0.15)
        if metrics['feature_similarity'].get('available'):
            feat_sim = metrics['feature_similarity']['cosine_similarity']
            scores.append(feat_sim * 100)
            weights.append(0.15)
        
        # Calculate weighted average
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalize weights
        composite = float(np.dot(scores, weights))
        
        return {
            'score': composite,
            'grade': self._get_grade(composite),
            'components': {
                'ssim_contribution': float(scores[0] * weights[0]) if len(scores) > 0 else 0,
                'sharpness_contribution': float(scores[1] * weights[1]) if len(scores) > 1 else 0,
                'color_contribution': float(scores[2] * weights[2]) if len(scores) > 2 else 0,
                'edge_contribution': float(scores[3] * weights[3]) if len(scores) > 3 else 0,
                'texture_contribution': float(scores[4] * weights[4]) if len(scores) > 4 else 0,
            }
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A (Excellent)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Fair)"
        elif score >= 60:
            return "D (Poor)"
        else:
            return "F (Very Poor)"
    
    def _print_summary(self, metrics: Dict):
        """Print a formatted summary of metrics"""
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)
        
        print(f"\nCOMPOSITE QUALITY SCORE: {metrics['composite_score']['score']:.2f}/100")
        print(f"   Grade: {metrics['composite_score']['grade']}")
        
        print(f"\nSTRUCTURAL SIMILARITY (SSIM): {metrics['ssim']['overall']:.4f}")
        print(f"   {metrics['ssim']['interpretation']}")
        
        print(f"\nPEAK SIGNAL-TO-NOISE RATIO: {metrics['psnr']['psnr_db']:.2f} dB")
        print(f"   {metrics['psnr']['interpretation']}")
        
        if metrics['lpips'].get('available'):
            print(f"\nPERCEPTUAL SIMILARITY (LPIPS): {metrics['lpips']['score']:.4f}")
            print(f"   {metrics['lpips']['interpretation']}")
        
        print(f"\nCOLOR CORRELATION: {metrics['color_metrics']['color_correlation']:.4f}")
        
        print(f"\nEDGE PRESERVATION IoU: {metrics['edge_preservation']['edge_iou']:.4f}")
        
        print(f"\nBASIC QUALITY:")
        print(f"   - Sharpness: {metrics['basic_quality']['sharpness']:.2f}")
        print(f"   - Brightness: {metrics['basic_quality']['brightness']:.2f}")
        print(f"   - Contrast: {metrics['basic_quality']['contrast']:.2f}")
        
        if metrics['feature_similarity'].get('available'):
            print(f"\nDEEP FEATURE SIMILARITY: {metrics['feature_similarity']['cosine_similarity']:.4f}")
            print(f"   {metrics['feature_similarity']['interpretation']}")
        
        print("\n" + "="*70)


def main():
    """CLI interface for evaluation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Evaluate virtual try-on quality with comprehensive metrics'
    )
    parser.add_argument('--generated', required=True, help='Path to generated try-on image')
    parser.add_argument('--person', required=True, help='Path to original person image')
    parser.add_argument('--cloth', required=True, help='Path to cloth/garment image')
    parser.add_argument('--output', default=None, help='Path to save metrics JSON')
    
    args = parser.parse_args()
    
    evaluator = VirtualTryOnEvaluator()
    metrics = evaluator.evaluate_tryon(
        generated_image_path=args.generated,
        reference_person_path=args.person,
        reference_cloth_path=args.cloth,
        output_json_path=args.output or 'evaluation_metrics.json'
    )
    
    print("\n[COMPLETE] Evaluation complete!")


if __name__ == "__main__":
    main()
