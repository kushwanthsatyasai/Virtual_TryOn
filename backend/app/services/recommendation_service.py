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
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text

logger = logging.getLogger(__name__)


def _rollback_db_session_safe(db: Session) -> None:
    try:
        db.rollback()
    except Exception:
        pass


def _first_color_from_db_value(cols_val) -> str:
    if cols_val is None:
        return "unknown"
    if isinstance(cols_val, list):
        return str(cols_val[0]).lower() if cols_val else "unknown"
    if isinstance(cols_val, str):
        try:
            arr = json.loads(cols_val)
            if isinstance(arr, list) and arr:
                return str(arr[0]).lower()
        except (json.JSONDecodeError, TypeError):
            if cols_val.strip():
                return cols_val.strip().lower()
    return "unknown"


def _product_row_from_mapping(row) -> Optional[Dict]:
    if row is None:
        return None
    d = dict(row)
    d["color_guess"] = _first_color_from_db_value(d.get("colors"))
    return d


def _sql_fetch_product_by_id(db: Session, pid: int) -> Optional[Dict]:
    try:
        r = db.execute(
            text(
                "SELECT id, name, category, brand, subcategory, colors, price, main_image_url "
                "FROM products WHERE id = :pid AND (is_active = true OR is_active IS NULL)"
            ),
            {"pid": pid},
        ).mappings().first()
        return _product_row_from_mapping(r)
    except Exception as e:
        logger.debug("SQL product by id failed: %s", e)
        _rollback_db_session_safe(db)
        return None


def _sql_fetch_product_by_name(db: Session, name: str) -> Optional[Dict]:
    try:
        r = db.execute(
            text(
                "SELECT id, name, category, brand, subcategory, colors, price, main_image_url "
                "FROM products WHERE lower(trim(name)) = lower(trim(:name)) "
                "AND (is_active = true OR is_active IS NULL) LIMIT 1"
            ),
            {"name": name},
        ).mappings().first()
        return _product_row_from_mapping(r)
    except Exception as e:
        logger.debug("SQL product by name failed: %s", e)
        _rollback_db_session_safe(db)
        return None


def _sql_user_favorite_product_rows(db: Session, user_id: int) -> List[Dict]:
    try:
        rows = db.execute(
            text(
                """
                SELECT p.id, p.name, p.category, p.brand, p.subcategory, p.colors, p.price, p.main_image_url
                FROM user_favorites uf
                JOIN products p ON p.id = uf.product_id
                WHERE uf.user_id = :uid
                """
            ),
            {"uid": user_id},
        ).mappings().all()
        return [_product_row_from_mapping(r) for r in rows if r is not None]
    except Exception as e:
        logger.debug("SQL user favorites join failed: %s", e)
        _rollback_db_session_safe(db)
        return []


def _sql_user_favorite_product_ids(db: Session, user_id: int) -> set:
    try:
        rows = db.execute(
            text("SELECT product_id FROM user_favorites WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchall()
        return {int(r[0]) for r in rows if r and r[0] is not None}
    except Exception as e:
        logger.debug("SQL user_favorites ids failed: %s", e)
        _rollback_db_session_safe(db)
        return set()


def _sql_count_user_favorites(db: Session, user_id: int) -> int:
    try:
        n = db.execute(
            text("SELECT COUNT(*) FROM user_favorites WHERE user_id = :uid"),
            {"uid": user_id},
        ).scalar()
        return int(n or 0)
    except Exception as e:
        logger.debug("SQL count favorites failed: %s", e)
        _rollback_db_session_safe(db)
        return 0


def _sql_fetch_products_catalog(db: Session, category_filter: Optional[str]) -> List[Dict]:
    try:
        if category_filter:
            rows = db.execute(
                text(
                    "SELECT id, name, category, brand, subcategory, colors, price, main_image_url "
                    "FROM products WHERE (is_active = true OR is_active IS NULL) "
                    "AND category = :cat LIMIT 200"
                ),
                {"cat": category_filter},
            ).mappings().all()
        else:
            rows = db.execute(
                text(
                    "SELECT id, name, category, brand, subcategory, colors, price, main_image_url "
                    "FROM products WHERE (is_active = true OR is_active IS NULL) LIMIT 200"
                )
            ).mappings().all()
        return [_product_row_from_mapping(r) for r in rows if r is not None]
    except Exception as e:
        logger.debug("SQL products catalog failed: %s", e)
        _rollback_db_session_safe(db)
        return []


# Frontend-aligned catalog (string ids). Used for try-on metadata enrichment and recommendations.
RECOMMENDATION_CATALOG: List[Dict] = [
    {"id": "balmain-shirt", "name": "Balmain Paris Baroque Print Shirt", "category": "top", "color": "white", "brand": "Balmain", "style": "designer", "price": 3049.00, "image_url": "assets/images/Balmain Paris Shirt.jpg"},
    {"id": "balmain-sweater", "name": "Balmain Monogram Knit Sweater", "category": "top", "color": "black", "brand": "Balmain", "style": "designer", "price": 429.00, "image_url": "assets/images/Balmain_Tshirt.jpg"},
    {"id": "blazer", "name": "Navy Blue Tailored Blazer", "category": "outerwear", "color": "navy", "brand": "Generic", "style": "formal", "price": 279.00, "image_url": "assets/images/Blazer.jpg"},
    {"id": "flowing-shirt", "name": "Soft Washed Blue Button-Up Shirt", "category": "top", "color": "blue", "brand": "Generic", "style": "casual", "price": 79.00, "image_url": "assets/images/Flowing Shirt.jpg"},
    {"id": "hoodie", "name": "Soho NYC Athletics Hoodie", "category": "outerwear", "color": "gray", "brand": "H&M", "style": "streetwear", "price": 69.00, "image_url": "assets/images/Hoodie H&M.jpg"},
    {"id": "jeans", "name": "Light Wash Wide-Leg Denim Jeans", "category": "bottom", "color": "blue", "brand": "Generic", "style": "casual", "price": 89.00, "image_url": "assets/images/Loose Jeans.jpg"},
    {"id": "suede-jacket", "name": "Mint Green Corduroy Trucker Jacket", "category": "outerwear", "color": "green", "brand": "Generic", "style": "casual", "price": 149.00, "image_url": "assets/images/Suede Jacket.jpeg"},
    {"id": "zara-shirt", "name": "State Park Striped Overshirt", "category": "top", "color": "multi", "brand": "Zara", "style": "casual", "price": 99.00, "image_url": "assets/images/ZARA_Shirt.jpg"},
    {"id": "zara-sweater", "name": "Oatmeal Ribbed Crewneck Sweater", "category": "top", "color": "beige", "brand": "Zara", "style": "casual", "price": 119.00, "image_url": "assets/images/Zara_Sweater.jpg"},
    {"id": "zara-tshirt", "name": "Classic Burgundy Crew Neck T-Shirt", "category": "top", "color": "burgundy", "brand": "Zara", "style": "casual", "price": 49.00, "image_url": "assets/images/ZARA_Tshirt.jpg"},
    {"id": "coat", "name": "Light Green Suede Trucker Jacket", "category": "outerwear", "color": "green", "brand": "Generic", "style": "casual", "price": 189.00, "image_url": "assets/images/Coat.png"},
    {"id": "stussy-tshirt", "name": "Black Stüssy Logo T-Shirt", "category": "top", "color": "black", "brand": "Stüssy", "style": "streetwear", "price": 59.00, "image_url": "assets/images/Tshirt_Web.jpg"},
]

RECOMMENDATION_CATALOG_BY_ID: Dict[str, Dict] = {p["id"]: p for p in RECOMMENDATION_CATALOG}


def _tryon_meta(tryon) -> Dict:
    """TryOnHistory stores JSON in column mapped as `metadata_` (not `.metadata`)."""
    return getattr(tryon, "metadata_", None) or {}


def build_tryon_metadata_for_product(
    db: Optional[Session],
    product_id: Optional[str],
    product_name: Optional[str],
    product_image_url: Optional[str],
) -> Optional[Dict]:
    """
    Build recommendation-friendly metadata when saving try-on history.
    Ensures item_id / category / color / brand exist for personalization.
    """
    if not (product_id or product_name or product_image_url):
        return None

    meta: Dict = {
        k: v
        for k, v in [
            ("product_id", product_id),
            ("product_name", product_name),
            ("product_image_url", product_image_url),
        ]
        if v
    }

    # Numeric DB product (UserFavorite / products table)
    if db is not None and product_id and str(product_id).isdigit():
        row = _sql_fetch_product_by_id(db, int(product_id))
        if row:
            meta["item_id"] = str(row["id"])
            meta["product_db_id"] = row["id"]
            meta["category"] = row.get("category") or "top"
            meta["brand"] = row.get("brand") or "unknown"
            meta["style"] = (row.get("subcategory") or "casual") if row.get("subcategory") else "casual"
            meta["color"] = row.get("color_guess") or "unknown"
            meta["price"] = float(row["price"]) if row.get("price") is not None else None
            return meta

    # String slug from in-app catalog
    if product_id and product_id in RECOMMENDATION_CATALOG_BY_ID:
        c = RECOMMENDATION_CATALOG_BY_ID[product_id]
        meta["item_id"] = c["id"]
        meta["category"] = c["category"]
        meta["color"] = c.get("color", "unknown")
        meta["brand"] = c.get("brand", "unknown")
        meta["style"] = c.get("style", "casual")
        meta["price"] = c.get("price")
        return meta

    # Flutter often sends product_name without product_id — map to static catalog
    if product_name:
        pn = product_name.strip().lower()
        for p in RECOMMENDATION_CATALOG:
            if p["name"].strip().lower() == pn:
                meta["item_id"] = p["id"]
                meta.setdefault("product_id", p["id"])
                meta["category"] = p["category"]
                meta["color"] = p.get("color", "unknown")
                meta["brand"] = p.get("brand", "unknown")
                meta["style"] = p.get("style", "casual")
                meta["price"] = p.get("price")
                return meta

    if db is not None and product_name:
        row = _sql_fetch_product_by_name(db, product_name.strip())
        if row:
            meta["item_id"] = str(row["id"])
            meta["product_db_id"] = row["id"]
            meta["category"] = row.get("category") or "top"
            meta["brand"] = row.get("brand") or "unknown"
            meta["style"] = row.get("subcategory") or "casual"
            meta["color"] = row.get("color_guess") or "unknown"
            meta["price"] = float(row["price"]) if row.get("price") is not None else None
            return meta

    meta["item_id"] = str(product_id or product_name or "unknown")
    meta.setdefault("category", "top")
    meta.setdefault("color", "unknown")
    meta.setdefault("brand", "unknown")
    meta.setdefault("style", "casual")
    return meta


def _resolve_image_path_for_features(url_or_path: Optional[str]) -> Optional[str]:
    """Map try-on stored cloth/result URL or relative path to a local file usable by PIL."""
    if not url_or_path:
        return None
    s = url_or_path.strip()
    if s.startswith("http://") or s.startswith("https://"):
        try:
            import requests

            resp = requests.get(s, timeout=20)
            if resp.status_code != 200:
                return None
            os.makedirs("temp", exist_ok=True)
            tmp = os.path.join("temp", f"rec_feat_{uuid.uuid4().hex}.png")
            with open(tmp, "wb") as f:
                f.write(resp.content)
            return tmp
        except Exception as e:
            logger.debug("Could not download image for features: %s", e)
            return None
    if os.path.isfile(s):
        return s
    rel = s.lstrip("/")
    if os.path.isfile(rel):
        return rel
    return None


def _item_id_from_tryon_meta(meta: Dict, tryon_id: int) -> str:
    return str(meta.get("item_id") or meta.get("product_id") or f"history_{tryon_id}")


def _infer_category_from_tryon(tryon, metadata: Dict) -> str:
    c = metadata.get("category")
    if c and c != "unknown":
        return c
    ct = (getattr(tryon, "cloth_type", None) or "").lower()
    if not ct:
        return "unknown"
    if "jean" in ct or "pant" in ct or "trouser" in ct:
        return "bottom"
    if "dress" in ct:
        return "dress"
    if "shoe" in ct or "sneaker" in ct or "boot" in ct:
        return "shoes"
    if "jacket" in ct or "coat" in ct or "blazer" in ct or "hoodie" in ct:
        return "outerwear"
    if "shirt" in ct or "top" in ct or "tee" in ct or "sweater" in ct:
        return "top"
    return "top"


def _infer_color_from_tryon(tryon, metadata: Dict) -> Optional[str]:
    if metadata.get("color"):
        return str(metadata["color"]).lower()
    cc = getattr(tryon, "cloth_color", None)
    if cc:
        return str(cc).lower()
    return None


def _infer_brand_from_tryon(tryon, metadata: Dict) -> Optional[str]:
    if metadata.get("brand"):
        return str(metadata["brand"])
    cb = getattr(tryon, "cloth_brand", None)
    return str(cb) if cb else None


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

        tried_items_set = self._get_tried_items(user_id)

        visual_active = self.use_visual_similarity
        if visual_active:
            try:
                from app.services.visual_similarity_service import get_visual_recommendation_service

                vs = get_visual_recommendation_service()
                se = getattr(vs, "search_engine", None)
                if not se or not getattr(se, "item_ids", None):
                    visual_active = False
            except Exception:
                visual_active = False

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
        
        # 6. Visual similarity (only if FAISS index has been built)
        if visual_active:
            visual_scores = self._visual_similarity_recommendations(user_id, category)
            for item_id, score in visual_scores.items():
                scores[item_id] += score * self.weights['visual_similarity']

        # Filter already tried items if requested
        if exclude_tried:
            scores = {k: v for k, v in scores.items() if k not in tried_items_set}
        
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

        # Cold start / low signal: fill from catalog so the UI always has items to show
        if len(recommendations) < min(limit, 8):
            seen_ids = {str(r.get("id", "")) for r in recommendations if r.get("id")}
            for p in RECOMMENDATION_CATALOG:
                if category and p.get("category") != category:
                    continue
                pid = p["id"]
                if pid in seen_ids:
                    continue
                if exclude_tried and pid in tried_items_set:
                    continue
                row = dict(p)
                row["image"] = row.get("image_url", "")
                recommendations.append(
                    {
                        **row,
                        "recommendation_score": 0.05,
                        "reason": "Popular styles you might like",
                    }
                )
                seen_ids.add(pid)
                if len(recommendations) >= limit:
                    break

        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations[:limit]
    
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
            metadata = _tryon_meta(tryon)
            cat = _infer_category_from_tryon(tryon, metadata)
            categories[cat] += 1
            col = _infer_color_from_tryon(tryon, metadata)
            if col:
                colors[col] += 1
            if metadata.get("style"):
                styles[metadata.get("style")] += 1
            br = _infer_brand_from_tryon(tryon, metadata)
            if br:
                brands[br] += 1
        
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
        scores = defaultdict(float)

        fav_rows = _sql_user_favorite_product_rows(self.db, user_id)
        if not fav_rows:
            return scores

        favorite_items = []
        for prod in fav_rows:
            if not prod or prod.get("id") is None:
                continue
            favorite_items.append(
                {
                    "item_id": str(prod["id"]),
                    "category": prod.get("category"),
                    "color": prod.get("color_guess") or "unknown",
                    "brand": prod.get("brand") or "unknown",
                    "style": prod.get("subcategory") or "casual",
                }
            )
        
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

        scores = defaultdict(float)

        similar_users = self._find_similar_users(user_id, limit=10)

        if not similar_users:
            return scores

        for similar_user_id, similarity_score in similar_users:
            their_tryons = (
                self.db.query(TryOnHistory)
                .filter(
                    and_(
                        TryOnHistory.user_id == similar_user_id,
                        TryOnHistory.created_at >= datetime.utcnow() - timedelta(days=60),
                    )
                )
                .limit(15)
                .all()
            )

            their_fav_ids = _sql_user_favorite_product_ids(self.db, similar_user_id)

            for tryon in their_tryons:
                metadata = _tryon_meta(tryon)
                item_id = _item_id_from_tryon_meta(metadata, tryon.id)

                is_favorite = False
                db_pid = metadata.get("product_db_id")
                if db_pid is not None and int(db_pid) in their_fav_ids:
                    is_favorite = True
                elif metadata.get("product_id") and str(metadata.get("product_id")).isdigit():
                    if int(metadata["product_id"]) in their_fav_ids:
                        is_favorite = True

                base_score = 0.8 if is_favorite else 0.5

                if category is None or metadata.get("category") == category:
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
            metadata = _tryon_meta(tryon)
            item_id = _item_id_from_tryon_meta(metadata, tryon.id)

            # Filter by category if specified
            if category is None or metadata.get("category") == category:
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
                cloth_u = getattr(tryon, "cloth_image_url", None) or ""
                result_u = getattr(tryon, "result_image_url", None) or ""
                image_path = _resolve_image_path_for_features(cloth_u) or _resolve_image_path_for_features(result_u)

                if image_path:
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
            metadata = _tryon_meta(tryon)
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
                metadata = _tryon_meta(tryon)
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
    
    def _all_catalog_clothing_items(self, category_filter: Optional[str] = None) -> List[ClothingItem]:
        """Merge static RECOMMENDATION_CATALOG with active rows from `products` table."""
        items: List[ClothingItem] = []
        seen: set = set()

        for p in RECOMMENDATION_CATALOG:
            if category_filter and p.get("category") != category_filter:
                continue
            pid = p["id"]
            if pid in seen:
                continue
            seen.add(pid)
            items.append(
                ClothingItem(
                    item_id=pid,
                    name=p["name"],
                    category=p["category"],
                    color=p.get("color"),
                    brand=p.get("brand"),
                    price=p.get("price"),
                    image_url=p.get("image_url"),
                    style=p.get("style"),
                )
            )

        for row in _sql_fetch_products_catalog(self.db, category_filter):
            if not row or row.get("id") is None:
                continue
            cid = str(row["id"])
            if cid in seen:
                continue
            items.append(
                ClothingItem(
                    item_id=cid,
                    name=row.get("name") or "",
                    category=row.get("category") or "top",
                    color=row.get("color_guess") or "unknown",
                    brand=row.get("brand"),
                    price=row.get("price"),
                    image_url=row.get("main_image_url"),
                    style=row.get("subcategory") or "casual",
                )
            )
            seen.add(cid)

        return items

    def _find_similar_items(
        self,
        categories: List[str] = None,
        colors: List[str] = None,
        styles: List[str] = None,
        brands: List[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[ClothingItem]:
        categories = [c for c in (categories or []) if c and c != "unknown"]
        colors = [c for c in (colors or []) if c and c != "unknown"]
        styles = [s for s in (styles or []) if s and s != "unknown"]
        brands = [b for b in (brands or []) if b and b != "unknown"]

        all_items = self._all_catalog_clothing_items(category_filter)
        if not any([categories, colors, styles, brands]):
            return all_items[:25]

        out: List[ClothingItem] = []
        seen_ids: set = set()
        for item in all_items:
            match = False
            if categories and item.category in categories:
                match = True
            if colors and item.color and item.color in colors:
                match = True
            if styles and item.style and item.style in styles:
                match = True
            if brands and item.brand and item.brand in brands:
                match = True
            if match and item.item_id not in seen_ids:
                seen_ids.add(item.item_id)
                out.append(item)

        return out if out else all_items[:20]

    def _find_items_by_categories(
        self,
        categories: List[str],
        category_filter: Optional[str] = None,
    ) -> List[ClothingItem]:
        cats = {c for c in categories if c}
        all_items = self._all_catalog_clothing_items(category_filter)
        return [i for i in all_items if i.category in cats]

    def _get_tried_items(self, user_id: int) -> set:
        """Get set of item IDs user has already tried"""
        from app.models.tryon_history import TryOnHistory

        tryons = self.db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).all()

        tried = set()
        for tryon in tryons:
            metadata = _tryon_meta(tryon)
            tried.add(_item_id_from_tryon_meta(metadata, tryon.id))

        return tried

    def _get_item_details(self, item_id: str) -> Optional[Dict]:
        """Resolve item by string catalog id, product name, or numeric DB product id."""
        by_id = {p["id"]: p for p in RECOMMENDATION_CATALOG}
        if item_id in by_id:
            out = dict(by_id[item_id])
            out.setdefault("image", out.get("image_url", ""))
            return out
        by_name = {p["name"]: p for p in RECOMMENDATION_CATALOG}
        if item_id in by_name:
            out = dict(by_name[item_id])
            out.setdefault("image", out.get("image_url", ""))
            return out
        if item_id.isdigit():
            row = _sql_fetch_product_by_id(self.db, int(item_id))
            if row:
                img = row.get("main_image_url") or ""
                return {
                    "id": str(row["id"]),
                    "name": row.get("name", ""),
                    "category": row.get("category", "top"),
                    "price": row.get("price", 0),
                    "image_url": img,
                    "image": img,
                }
        return None
    
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

        # Get all user activity
        tryons = (
            self.db.query(TryOnHistory)
            .filter(TryOnHistory.user_id == user_id)
            .all()
        )

        favorites = _sql_count_user_favorites(self.db, user_id)
        
        # Analyze preferences
        categories = Counter()
        colors = Counter()
        brands = Counter()
        styles = Counter()
        price_range = []
        
        for tryon in tryons:
            metadata = _tryon_meta(tryon)
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
