"""
Visual Similarity Service for Fashion Recommendation
===================================================
Uses ResNet-based deep learning to find visually similar clothing items.

Based on: https://github.com/khanhnamle1994/fashion-recommendation
Modern implementation using PyTorch and pre-trained ResNet50.
"""
import logging
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import pickle
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import faiss  # For efficient similarity search

logger = logging.getLogger(__name__)


class FashionFeatureExtractor:
    """
    Extract visual features from fashion images using pre-trained ResNet50.
    Features can be used for similarity search and visual recommendations.
    """
    
    def __init__(self, use_gpu: bool = True):
        """
        Initialize the feature extractor.
        
        Args:
            use_gpu: Whether to use GPU if available
        """
        self.device = torch.device(
            'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        )
        logger.info(f"Visual similarity using device: {self.device}")
        
        # Load pre-trained ResNet50 (similar to the original implementation)
        self.model = models.resnet50(pretrained=True)
        
        # Remove the final classification layer to get features
        # We use the avgpool layer output (2048-dimensional features)
        self.model = nn.Sequential(*list(self.model.children())[:-1])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Define image preprocessing (ImageNet normalization)
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        logger.info("Fashion feature extractor initialized successfully")
    
    def extract_features(self, image_path: str) -> np.ndarray:
        """
        Extract visual features from a single image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Feature vector (2048-dimensional numpy array)
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
            
            # Flatten and convert to numpy
            features = features.cpu().numpy().flatten()
            
            # L2 normalize for better similarity comparison
            features = features / np.linalg.norm(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from {image_path}: {e}")
            return np.zeros(2048)  # Return zero vector on error
    
    def extract_features_batch(self, image_paths: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Extract features from multiple images in batches (more efficient).
        
        Args:
            image_paths: List of image file paths
            batch_size: Number of images to process at once
            
        Returns:
            Feature matrix (N x 2048 numpy array)
        """
        all_features = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_tensors = []
            
            for path in batch_paths:
                try:
                    image = Image.open(path).convert('RGB')
                    tensor = self.preprocess(image)
                    batch_tensors.append(tensor)
                except Exception as e:
                    logger.error(f"Error loading {path}: {e}")
                    batch_tensors.append(torch.zeros(3, 224, 224))
            
            # Stack into batch
            batch = torch.stack(batch_tensors).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(batch)
            
            features = features.cpu().numpy().reshape(len(batch_paths), -1)
            
            # L2 normalize
            norms = np.linalg.norm(features, axis=1, keepdims=True)
            features = features / (norms + 1e-8)
            
            all_features.append(features)
        
        return np.vstack(all_features)


class VisualSimilaritySearchEngine:
    """
    Efficient similarity search engine using FAISS (Facebook AI Similarity Search).
    Finds k-nearest neighbors for visual fashion recommendation.
    """
    
    def __init__(self, feature_dim: int = 2048):
        """
        Initialize the search engine.
        
        Args:
            feature_dim: Dimension of feature vectors
        """
        self.feature_dim = feature_dim
        self.index = None
        self.item_ids = []
        self.metadata = {}
        
        # Use Inner Product (cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(feature_dim)
        
        logger.info(f"Visual similarity search engine initialized (dim={feature_dim})")
    
    def add_items(
        self,
        features: np.ndarray,
        item_ids: List[str],
        metadata: Optional[List[Dict]] = None
    ):
        """
        Add items to the search index.
        
        Args:
            features: Feature matrix (N x feature_dim)
            item_ids: List of item IDs corresponding to features
            metadata: Optional metadata for each item
        """
        # Ensure features are float32 (FAISS requirement)
        features = features.astype(np.float32)
        
        # Add to index
        self.index.add(features)
        self.item_ids.extend(item_ids)
        
        # Store metadata
        if metadata:
            for item_id, meta in zip(item_ids, metadata):
                self.metadata[item_id] = meta
        
        logger.info(f"Added {len(item_ids)} items to search index. Total: {len(self.item_ids)}")
    
    def search(
        self,
        query_features: np.ndarray,
        k: int = 10,
        include_distances: bool = True
    ) -> List[Dict]:
        """
        Search for k most similar items.
        
        Args:
            query_features: Query feature vector
            k: Number of similar items to return
            include_distances: Whether to include similarity scores
            
        Returns:
            List of similar items with IDs, scores, and metadata
        """
        if self.index is None or len(self.item_ids) == 0:
            logger.warning("Search index is empty")
            return []
        
        # Ensure correct shape and type
        query_features = query_features.reshape(1, -1).astype(np.float32)
        
        # Search
        distances, indices = self.index.search(query_features, min(k, len(self.item_ids)))
        
        # Format results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.item_ids):
                item_id = self.item_ids[idx]
                result = {
                    'item_id': item_id,
                    'similarity_score': float(distance),  # Cosine similarity (0-1)
                }
                
                # Add metadata if available
                if item_id in self.metadata:
                    result.update(self.metadata[item_id])
                
                results.append(result)
        
        return results
    
    def save(self, save_dir: str):
        """Save the search index and metadata to disk."""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(save_dir, 'faiss_index.bin'))
        
        # Save item IDs and metadata
        with open(os.path.join(save_dir, 'item_data.pkl'), 'wb') as f:
            pickle.dump({
                'item_ids': self.item_ids,
                'metadata': self.metadata
            }, f)
        
        logger.info(f"Search index saved to {save_dir}")
    
    def load(self, load_dir: str):
        """Load the search index and metadata from disk."""
        # Load FAISS index
        self.index = faiss.read_index(os.path.join(load_dir, 'faiss_index.bin'))
        
        # Load item IDs and metadata
        with open(os.path.join(load_dir, 'item_data.pkl'), 'rb') as f:
            data = pickle.load(f)
            self.item_ids = data['item_ids']
            self.metadata = data['metadata']
        
        logger.info(f"Search index loaded from {load_dir}. Items: {len(self.item_ids)}")


class VisualRecommendationService:
    """
    Complete visual recommendation service combining feature extraction and similarity search.
    """
    
    def __init__(self, index_dir: Optional[str] = None):
        """
        Initialize the visual recommendation service.
        
        Args:
            index_dir: Directory to load pre-built index from
        """
        self.feature_extractor = FashionFeatureExtractor()
        self.search_engine = VisualSimilaritySearchEngine()
        
        # Load pre-built index if available
        if index_dir and os.path.exists(index_dir):
            try:
                self.search_engine.load(index_dir)
                logger.info("Loaded pre-built visual similarity index")
            except Exception as e:
                logger.warning(f"Could not load index from {index_dir}: {e}")
    
    def get_similar_items_by_image(
        self,
        image_path: str,
        k: int = 10,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get visually similar items for a given image.
        
        Args:
            image_path: Path to query image
            k: Number of similar items to return
            category_filter: Optional category filter
            
        Returns:
            List of similar items with scores
        """
        # Extract features from query image
        query_features = self.feature_extractor.extract_features(image_path)
        
        # Search for similar items
        similar_items = self.search_engine.search(query_features, k=k * 2)  # Get more for filtering
        
        # Filter by category if specified
        if category_filter:
            similar_items = [
                item for item in similar_items
                if item.get('category') == category_filter
            ]
        
        # Return top k
        return similar_items[:k]
    
    def get_similar_items_by_id(
        self,
        item_id: str,
        k: int = 10,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get visually similar items for a given item ID.
        
        Args:
            item_id: ID of the item to find similar items for
            k: Number of similar items to return
            category_filter: Optional category filter
            
        Returns:
            List of similar items with scores
        """
        # Find the item's features in the index
        if item_id not in self.search_engine.item_ids:
            logger.warning(f"Item {item_id} not found in index")
            return []
        
        idx = self.search_engine.item_ids.index(item_id)
        
        # Get features
        query_features = self.search_engine.index.reconstruct(idx)
        
        # Search (exclude the query item itself)
        similar_items = self.search_engine.search(query_features, k=k + 1)
        similar_items = [item for item in similar_items if item['item_id'] != item_id]
        
        # Filter by category if specified
        if category_filter:
            similar_items = [
                item for item in similar_items
                if item.get('category') == category_filter
            ]
        
        return similar_items[:k]
    
    def build_index_from_catalog(
        self,
        catalog: List[Dict],
        image_dir: str,
        save_dir: Optional[str] = None
    ):
        """
        Build search index from a product catalog.
        
        Args:
            catalog: List of product dictionaries with 'id', 'image_path', etc.
            image_dir: Base directory for images
            save_dir: Optional directory to save the built index
        """
        logger.info(f"Building visual similarity index from {len(catalog)} items...")
        
        # Prepare image paths and metadata
        image_paths = []
        item_ids = []
        metadata = []
        
        for item in catalog:
            image_path = os.path.join(image_dir, item.get('image_path', ''))
            if os.path.exists(image_path):
                image_paths.append(image_path)
                item_ids.append(item['id'])
                metadata.append({
                    'name': item.get('name'),
                    'category': item.get('category'),
                    'brand': item.get('brand'),
                    'price': item.get('price'),
                    'image_url': item.get('image_url')
                })
        
        # Extract features in batches
        logger.info(f"Extracting features from {len(image_paths)} images...")
        features = self.feature_extractor.extract_features_batch(image_paths, batch_size=32)
        
        # Add to search engine
        self.search_engine.add_items(features, item_ids, metadata)
        
        # Save if requested
        if save_dir:
            self.search_engine.save(save_dir)
        
        logger.info("Visual similarity index built successfully!")
    
    def add_item_to_index(
        self,
        item_id: str,
        image_path: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a single item to the search index.
        
        Args:
            item_id: Unique item identifier
            image_path: Path to item image
            metadata: Optional metadata
        """
        # Extract features
        features = self.feature_extractor.extract_features(image_path)
        features = features.reshape(1, -1)
        
        # Add to index
        self.search_engine.add_items(
            features,
            [item_id],
            [metadata] if metadata else None
        )
        
        logger.info(f"Added item {item_id} to visual similarity index")


# Global service instance
_visual_rec_service = None


def get_visual_recommendation_service(index_dir: Optional[str] = "data/visual_index") -> VisualRecommendationService:
    """Get or create the visual recommendation service instance."""
    global _visual_rec_service
    
    if _visual_rec_service is None:
        _visual_rec_service = VisualRecommendationService(index_dir=index_dir)
    
    return _visual_rec_service
