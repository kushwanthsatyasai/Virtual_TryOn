"""
Recommendation Engine Service
=============================
AI-powered clothing recommendations based on:
- User try-on history
- Recent activity
- Style preferences
- Similar users (collaborative filtering)
- Item similarity (content-based filtering)
"""
import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

logger = logging.getLogger(__name__)


class ClothingItem:
    """Represents a clothing item for recommendations"""
    def __init__(
        self,
        item_id: str,
        name: str,
        category: str,
        color: str = None,
        brand: str = None,
        price: float = None,
        image_url: str = None,
        tags: List[str] = None,
        style: str = None
    ):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.color = color
        self.brand = brand
        self.price = price
        self.image_url = image_url
        self.tags = tags or []
        self.style = style


class RecommendationEngine:
    """
    Multi-strategy recommendation engine combining:
    1. Content-based filtering (similar items)
    2. Collaborative filtering (similar users)
    3. Activity-based recommendations
    4. Trending items
    5. Style matching
    6. Visual similarity (ResNet-based deep learning)
    """
    
    def __init__(self, db: Session, use_visual_similarity: bool = True):
        self.db = db
        self.use_visual_similarity = use_visual_similarity
        
        # Adjust weights based on whether visual similarity is enabled
        if use_visual_similarity:
            self.weights = {
                'try_on_history': 0.25,
                'favorites': 0.20,
                'wardrobe': 0.15,
                'similar_users': 0.15,
                'trending': 0.10,
                'visual_similarity': 0.15  # New visual similarity weight
            }
        else:
            self.weights = {
                'try_on_history': 0.30,
                'favorites': 0.25,
                'wardrobe': 0.20,
                'similar_users': 0.15,
                'trending': 0.10
            }
    
    def get_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        category: Optional[str] = None,
        exclude_tried: bool = False
    ) -> List[Dict]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User ID
            limit: Number of recommendations
            category: Filter by category (optional)
            exclude_tried: Exclude items already tried
            
        Returns:
            List of recommended items with scores
        """
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Collect scores from different strategies
        scores = defaultdict(float)
        
        # 1. Content-based: Items similar to user's history
        content_scores = self._content_based_recommendations(user_id, category)
        for item_id, score in content_scores.items():
            scores[item_id] += score * self.weights['try_on_history']
        
        # 2. Favorites-based: Items similar to favorites
        favorite_scores = self._favorite_based_recommendations(user_id, category)
        for item_id, score in favorite_scores.items():
            scores[item_id] += score * self.weights['favorites']
        
        # 3. Wardrobe-based: Complete the wardrobe
        wardrobe_scores = self._wardrobe_based_recommendations(user_id, category)
        for item_id, score in wardrobe_scores.items():
            scores[item_id] += score * self.weights['wardrobe']
        
        # 4. Collaborative filtering: Similar users
        collab_scores = self._collaborative_filtering(user_id, category)
        for item_id, score in collab_scores.items():
            scores[item_id] += score * self.weights['similar_users']
        
        # 5. Trending items
        trending_scores = self._trending_items(category)
        for item_id, score in trending_scores.items():
            scores[item_id] += score * self.weights['trending']
        
        # 6. Visual similarity (if enabled)
        if self.use_visual_similarity:
            visual_scores = self._visual_similarity_recommendations(user_id, category)
            for item_id, score in visual_scores.items():
                scores[item_id] += score * self.weights['visual_similarity']
        
        # Filter already tried items if requested
        if exclude_tried:
            tried_items = self._get_tried_items(user_id)
            scores = {k: v for k, v in scores.items() if k not in tried_items}
        
        # Sort by score and return top N
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_items[:limit]
        
        # Get item details
        recommendations = []
        for item_id, score in top_items:
            item_details = self._get_item_details(item_id)
            if item_details:
                recommendations.append({
                    **item_details,
                    'recommendation_score': round(score, 3),
                    'reason': self._generate_reason(user_id, item_id)
                })
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _content_based_recommendations(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Recommend items similar to user's try-on history
        Uses: category, color, style, brand similarity
        """
        from app.models.tryon_history import TryOnHistory
        
        scores = defaultdict(float)
        
        # Get recent try-ons (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_tryons = (
            self.db.query(TryOnHistory)
            .filter(
                and_(
                    TryOnHistory.user_id == user_id,
                    TryOnHistory.created_at >= cutoff_date
                )
            )
            .order_by(desc(TryOnHistory.created_at))
            .limit(20)
            .all()
        )
        
        if not recent_tryons:
            return scores
        
        # Extract preferences
        categories = Counter()
        colors = Counter()
        styles = Counter()
        brands = Counter()
        
        for tryon in recent_tryons:
            metadata = tryon.metadata or {}
            categories[metadata.get('category', 'unknown')] += 1
            if metadata.get('color'):
                colors[metadata.get('color')] += 1
            if metadata.get('style'):
                styles[metadata.get('style')] += 1
            if metadata.get('brand'):
                brands[metadata.get('brand')] += 1
        
        # Get similar items from wardrobe/catalog
        # (In production, query your product database)
        similar_items = self._find_similar_items(
            categories=list(categories.keys()),
            colors=list(colors.keys()),
            styles=list(styles.keys()),
            brands=list(brands.keys()),
            category_filter=category
        )
        
        # Score based on similarity
        for item in similar_items:
            score = 0.0
            
            # Category match (highest weight)
            if item.category in categories:
                score += 0.4 * (categories[item.category] / len(recent_tryons))
            
            # Color match
            if item.color in colors:
                score += 0.3 * (colors[item.color] / len(recent_tryons))
            
            # Style match
            if item.style in styles:
                score += 0.2 * (styles[item.style] / len(recent_tryons))
            
            # Brand match
            if item.brand in brands:
                score += 0.1 * (brands[item.brand] / len(recent_tryons))
            
            if score > 0:
                scores[item.item_id] = score
        
        return scores
    
    def _favorite_based_recommendations(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Recommend items similar to user's favorites
        """
        from app.models.favorites import Favorite
        
        scores = defaultdict(float)
        
        # Get user's favorites
        favorites = (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .all()
        )
        
        if not favorites:
            return scores
        
        # Get metadata from favorited try-ons
        favorite_items = []
        for fav in favorites:
            if fav.tryon_history:
                metadata = fav.tryon_history.metadata or {}
                favorite_items.append(metadata)
        
        # Extract common characteristics
        categories = Counter(item.get('category') for item in favorite_items if item.get('category'))
        colors = Counter(item.get('color') for item in favorite_items if item.get('color'))
        styles = Counter(item.get('style') for item in favorite_items if item.get('style'))
        
        # Find similar items
        similar_items = self._find_similar_items(
            categories=list(categories.keys()),
            colors=list(colors.keys()),
            styles=list(styles.keys()),
            category_filter=category
        )
        
        for item in similar_items:
            score = 0.0
            if item.category in categories:
                score += 0.5
            if item.color in colors:
                score += 0.3
            if item.style in styles:
                score += 0.2
            
            if score > 0:
                scores[item.item_id] = score
        
        return scores
    
    def _wardrobe_based_recommendations(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Recommend items that complement user's wardrobe
        """
        from app.models.wardrobe import WardrobeItem
        
        scores = defaultdict(float)
        
        # Get user's wardrobe
        wardrobe = (
            self.db.query(WardrobeItem)
            .filter(WardrobeItem.user_id == user_id)
            .all()
        )
        
        if not wardrobe:
            return scores
        
        # Analyze wardrobe gaps
        wardrobe_categories = Counter(item.category for item in wardrobe)
        
        # Recommend complementary items
        # E.g., if user has many tops, recommend bottoms
        complementary_map = {
            'top': ['bottom', 'outerwear', 'dress'],
            'bottom': ['top', 'shoes', 'outerwear'],
            'dress': ['shoes', 'outerwear', 'accessories'],
            'outerwear': ['top', 'bottom'],
            'shoes': ['top', 'bottom', 'dress']
        }
        
        # Find what's missing
        complementary_categories = []
        for cat, count in wardrobe_categories.items():
            if cat in complementary_map:
                complementary_categories.extend(complementary_map[cat])
        
        # Get items in complementary categories
        complementary_items = self._find_items_by_categories(
            complementary_categories,
            category_filter=category
        )
        
        for item in complementary_items:
            scores[item.item_id] = 0.7  # High score for filling gaps
        
        return scores
    
    def _collaborative_filtering(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Recommend based on similar users' preferences
        "Users who tried similar items also tried..."
        """
        from app.models.tryon_history import TryOnHistory
        from app.models.favorites import Favorite
        
        scores = defaultdict(float)
        
        # Find users with similar taste
        similar_users = self._find_similar_users(user_id, limit=10)
        
        if not similar_users:
            return scores
        
        # Get what similar users tried and liked
        for similar_user_id, similarity_score in similar_users:
            # Get their recent try-ons
            their_tryons = (
                self.db.query(TryOnHistory)
                .filter(
                    and_(
                        TryOnHistory.user_id == similar_user_id,
                        TryOnHistory.created_at >= datetime.utcnow() - timedelta(days=60)
                    )
                )
                .limit(15)
                .all()
            )
            
            # Get their favorites
            their_favorites = (
                self.db.query(Favorite)
                .filter(Favorite.user_id == similar_user_id)
                .all()
            )
            
            # Score items from similar users
            for tryon in their_tryons:
                metadata = tryon.metadata or {}
                item_id = metadata.get('item_id', f"item_{tryon.id}")
                
                # Higher score if they favorited it
                is_favorite = any(f.tryon_history_id == tryon.id for f in their_favorites)
                base_score = 0.8 if is_favorite else 0.5
                
                scores[item_id] += base_score * similarity_score
        
        return scores
    
    def _trending_items(self, category: Optional[str] = None) -> Dict[str, float]:
        """
        Recommend trending items (most tried in last week)
        """
        from app.models.tryon_history import TryOnHistory
        
        scores = defaultdict(float)
        
        # Get try-ons from last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_tryons = (
            self.db.query(TryOnHistory)
            .filter(TryOnHistory.created_at >= cutoff_date)
            .all()
        )
        
        # Count item popularity
        item_counts = Counter()
        for tryon in recent_tryons:
            metadata = tryon.metadata or {}
            item_id = metadata.get('item_id', f"item_{tryon.id}")
            
            # Filter by category if specified
            if category is None or metadata.get('category') == category:
                item_counts[item_id] += 1
        
        # Normalize scores
        max_count = max(item_counts.values()) if item_counts else 1
        for item_id, count in item_counts.items():
            scores[item_id] = count / max_count
        
        return scores
    
    def _visual_similarity_recommendations(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Recommend items based on visual similarity to user's try-on history.
        Uses deep learning (ResNet) to find visually similar clothing items.
        """
        from app.models.tryon_history import TryOnHistory
        
        scores = defaultdict(float)
        
        try:
            # Import visual similarity service (lazy import to avoid circular dependencies)
            from app.services.visual_similarity_service import get_visual_recommendation_service
            
            visual_service = get_visual_recommendation_service()
            
            # Get user's recent try-ons (last 14 days for visual analysis)
            cutoff_date = datetime.utcnow() - timedelta(days=14)
            recent_tryons = (
                self.db.query(TryOnHistory)
                .filter(
                    and_(
                        TryOnHistory.user_id == user_id,
                        TryOnHistory.created_at >= cutoff_date
                    )
                )
                .order_by(desc(TryOnHistory.created_at))
                .limit(5)  # Top 5 recent try-ons
                .all()
            )
            
            if not recent_tryons:
                return scores
            
            # For each try-on, find visually similar items
            all_similar = {}
            for tryon in recent_tryons:
                # Use the cloth image if available
                image_path = None
                if hasattr(tryon, 'cloth_image_path') and tryon.cloth_image_path:
                    image_path = tryon.cloth_image_path
                elif hasattr(tryon, 'result_image_path') and tryon.result_image_path:
                    image_path = tryon.result_image_path
                
                if image_path and os.path.exists(image_path):
                    try:
                        similar_items = visual_service.get_similar_items_by_image(
                            image_path=image_path,
                            k=5,
                            category_filter=category
                        )
                        
                        # Add to scores (higher weight for more recent try-ons)
                        recency_weight = 1.0  # Could decay based on age
                        for item in similar_items:
                            item_id = item.get('item_id')
                            similarity = item.get('similarity_score', 0)
                            
                            if item_id:
                                # Combine similarity score with recency
                                if item_id not in all_similar:
                                    all_similar[item_id] = similarity * recency_weight
                                else:
                                    # Average if item appears multiple times
                                    all_similar[item_id] = (all_similar[item_id] + similarity * recency_weight) / 2
                    
                    except Exception as e:
                        logger.debug(f"Visual similarity lookup failed for tryon {tryon.id}: {e}")
                        continue
            
            # Normalize scores to 0-1 range
            if all_similar:
                max_score = max(all_similar.values())
                for item_id, score in all_similar.items():
                    scores[item_id] = score / max_score if max_score > 0 else 0
            
            logger.debug(f"Visual similarity found {len(scores)} recommendations for user {user_id}")
            
        except ImportError:
            logger.warning("Visual similarity service not available (faiss-cpu not installed?)")
        except Exception as e:
            logger.error(f"Error in visual similarity recommendations: {e}")
        
        return scores
    
    def _find_similar_users(self, user_id: int, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Find users with similar preferences
        Returns: List of (user_id, similarity_score)
        """
        from app.models.tryon_history import TryOnHistory
        from app.models.favorites import Favorite
        
        # Get current user's preferences
        user_tryons = (
            self.db.query(TryOnHistory)
            .filter(TryOnHistory.user_id == user_id)
            .limit(50)
            .all()
        )
        
        if not user_tryons:
            return []
        
        # Extract user's preference vector
        user_categories = Counter()
        user_styles = Counter()
        for tryon in user_tryons:
            metadata = tryon.metadata or {}
            user_categories[metadata.get('category', 'unknown')] += 1
            user_styles[metadata.get('style', 'unknown')] += 1
        
        # Find other users
        all_users = (
            self.db.query(TryOnHistory.user_id)
            .filter(TryOnHistory.user_id != user_id)
            .distinct()
            .all()
        )
        
        similarities = []
        for (other_user_id,) in all_users[:50]:  # Limit for performance
            # Get other user's preferences
            other_tryons = (
                self.db.query(TryOnHistory)
                .filter(TryOnHistory.user_id == other_user_id)
                .limit(50)
                .all()
            )
            
            other_categories = Counter()
            other_styles = Counter()
            for tryon in other_tryons:
                metadata = tryon.metadata or {}
                other_categories[metadata.get('category', 'unknown')] += 1
                other_styles[metadata.get('style', 'unknown')] += 1
            
            # Calculate similarity (cosine similarity on category/style vectors)
            similarity = self._calculate_similarity(
                user_categories, user_styles,
                other_categories, other_styles
            )
            
            if similarity > 0.3:  # Threshold for similarity
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def _calculate_similarity(
        self,
        user_cat: Counter,
        user_style: Counter,
        other_cat: Counter,
        other_style: Counter
    ) -> float:
        """Calculate cosine similarity between two users"""
        # Combine categories and styles
        all_keys = set(user_cat.keys()) | set(other_cat.keys()) | \
                   set(user_style.keys()) | set(other_style.keys())
        
        if not all_keys:
            return 0.0
        
        # Create vectors
        vec1 = []
        vec2 = []
        for key in all_keys:
            vec1.append(user_cat.get(key, 0) + user_style.get(key, 0))
            vec2.append(other_cat.get(key, 0) + other_style.get(key, 0))
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _find_similar_items(
        self,
        categories: List[str] = None,
        colors: List[str] = None,
        styles: List[str] = None,
        brands: List[str] = None,
        category_filter: Optional[str] = None
    ) -> List[ClothingItem]:
        """
        Find items matching given criteria
        In production, this would query your product catalog/database
        """
        # Mock implementation - replace with actual product database query
        mock_items = [
            ClothingItem("item_001", "Classic T-Shirt", "top", "white", "Nike", 29.99, tags=["casual", "basic"]),
            ClothingItem("item_002", "Denim Jeans", "bottom", "blue", "Levi's", 79.99, tags=["casual", "denim"]),
            ClothingItem("item_003", "Blazer", "outerwear", "black", "Zara", 99.99, tags=["formal", "professional"]),
            ClothingItem("item_004", "Summer Dress", "dress", "floral", "H&M", 49.99, tags=["casual", "summer"]),
            ClothingItem("item_005", "Sneakers", "shoes", "white", "Adidas", 89.99, tags=["casual", "sport"]),
        ]
        
        # Filter by criteria
        filtered = []
        for item in mock_items:
            if category_filter and item.category != category_filter:
                continue
            
            if categories and item.category in categories:
                filtered.append(item)
            elif colors and item.color in colors:
                filtered.append(item)
            elif styles and item.style in styles:
                filtered.append(item)
            elif brands and item.brand in brands:
                filtered.append(item)
        
        return filtered
    
    def _find_items_by_categories(
        self,
        categories: List[str],
        category_filter: Optional[str] = None
    ) -> List[ClothingItem]:
        """Find items in specified categories"""
        # Mock implementation
        mock_items = [
            ClothingItem("item_006", "Hoodie", "outerwear", "gray", "Gap", 59.99),
            ClothingItem("item_007", "Chinos", "bottom", "khaki", "Uniqlo", 49.99),
            ClothingItem("item_008", "Polo Shirt", "top", "navy", "Ralph Lauren", 89.99),
        ]
        
        return [item for item in mock_items if item.category in categories]
    
    def _get_tried_items(self, user_id: int) -> set:
        """Get set of item IDs user has already tried"""
        from app.models.tryon_history import TryOnHistory
        
        tryons = (
            self.db.query(TryOnHistory)
            .filter(TryOnHistory.user_id == user_id)
            .all()
        )
        
        tried = set()
        for tryon in tryons:
            metadata = tryon.metadata or {}
            item_id = metadata.get('item_id', f"item_{tryon.id}")
            tried.add(item_id)
        
        return tried
    
    def _get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get item details by ID (mock implementation)"""
        # In production, query your product database
        mock_database = {
            "item_001": {"id": "item_001", "name": "Classic T-Shirt", "category": "top", "price": 29.99, "brand": "Nike", "image": "/static/items/001.jpg"},
            "item_002": {"id": "item_002", "name": "Denim Jeans", "category": "bottom", "price": 79.99, "brand": "Levi's", "image": "/static/items/002.jpg"},
            # Add more items...
        }
        return mock_database.get(item_id)
    
    def _generate_reason(self, user_id: int, item_id: str) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = [
            "Based on your recent try-ons",
            "Similar to your favorites",
            "Complements your wardrobe",
            "Trending this week",
            "Popular with similar users"
        ]
        # In production, determine actual reason based on scoring
        return reasons[hash(item_id) % len(reasons)]
    
    def get_user_style_profile(self, user_id: int) -> Dict:
        """
        Get user's style profile for personalization
        """
        from app.models.tryon_history import TryOnHistory
        from app.models.favorites import Favorite
        
        # Get all user activity
        tryons = (
            self.db.query(TryOnHistory)
            .filter(TryOnHistory.user_id == user_id)
            .all()
        )
        
        favorites = (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .count()
        )
        
        # Analyze preferences
        categories = Counter()
        colors = Counter()
        brands = Counter()
        styles = Counter()
        price_range = []
        
        for tryon in tryons:
            metadata = tryon.metadata or {}
            categories[metadata.get('category', 'unknown')] += 1
            if metadata.get('color'):
                colors[metadata.get('color')] += 1
            if metadata.get('brand'):
                brands[metadata.get('brand')] += 1
            if metadata.get('style'):
                styles[metadata.get('style')] += 1
            if metadata.get('price'):
                price_range.append(metadata.get('price'))
        
        # Calculate statistics
        avg_price = sum(price_range) / len(price_range) if price_range else 0
        
        return {
            'user_id': user_id,
            'total_tryons': len(tryons),
            'total_favorites': favorites,
            'favorite_categories': dict(categories.most_common(5)),
            'favorite_colors': dict(colors.most_common(5)),
            'favorite_brands': dict(brands.most_common(5)),
            'favorite_styles': dict(styles.most_common(5)),
            'average_price_preference': round(avg_price, 2),
            'price_range': {
                'min': min(price_range) if price_range else 0,
                'max': max(price_range) if price_range else 0
            }
        }
    
    def record_recommendation_interaction(
        self,
        user_id: int,
        item_id: str,
        interaction_type: str  # 'view', 'try', 'favorite', 'ignore'
    ):
        """Record user interaction with recommendation for learning"""
        # In production, store this in a recommendation_interactions table
        # This data can be used to improve recommendation quality over time
        logger.info(f"User {user_id} {interaction_type} item {item_id}")
        pass


# Service factory
def get_recommendation_service(db: Session) -> RecommendationEngine:
    """Get recommendation service instance"""
    return RecommendationEngine(db)
