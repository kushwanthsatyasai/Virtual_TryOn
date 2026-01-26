"""
Fashion Metadata Service
========================
Enhance products with rich fashion metadata without needing RAG databases.

This service provides:
- Style tags and categories
- Seasonal recommendations
- Occasion matching
- Care instructions
- Styling tips
- Color and pattern analysis
"""
import logging
from typing import List, Dict, Optional
from PIL import Image
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class FashionMetadataEnhancer:
    """
    Enhance product metadata with fashion knowledge.
    Simple rule-based system - no LLM or RAG database needed!
    """
    
    # Fashion knowledge base (can be extended with more data)
    STYLE_CATEGORIES = {
        'casual': ['t-shirt', 'jeans', 'sneakers', 'hoodie', 'shorts'],
        'formal': ['suit', 'blazer', 'dress shirt', 'tie', 'dress shoes'],
        'business-casual': ['chinos', 'polo', 'loafers', 'blouse'],
        'sporty': ['activewear', 'sneakers', 'joggers', 'sports bra'],
        'bohemian': ['maxi dress', 'flowy', 'floral', 'fringe'],
        'minimalist': ['simple', 'clean lines', 'neutral', 'monochrome'],
        'vintage': ['retro', 'classic', '80s', '90s', 'vintage'],
        'streetwear': ['oversized', 'graphic', 'hoodie', 'sneakers']
    }
    
    OCCASION_MAPPING = {
        'work': ['formal', 'business-casual', 'professional'],
        'casual': ['casual', 'relaxed', 'everyday'],
        'party': ['cocktail', 'evening', 'dressy'],
        'sport': ['athletic', 'activewear', 'sporty'],
        'wedding': ['formal', 'semi-formal', 'elegant'],
        'beach': ['casual', 'summer', 'resort'],
        'date': ['dressy', 'elegant', 'romantic']
    }
    
    SEASON_KEYWORDS = {
        'spring': ['light', 'floral', 'pastel', 'layering'],
        'summer': ['breathable', 'light', 'sleeveless', 'shorts'],
        'fall': ['layering', 'warm', 'earth tones', 'jacket'],
        'winter': ['warm', 'cozy', 'layered', 'insulated']
    }
    
    CARE_INSTRUCTIONS = {
        'cotton': 'Machine wash cold, tumble dry low. May shrink slightly.',
        'silk': 'Dry clean only or hand wash cold. Hang to dry.',
        'wool': 'Dry clean recommended. Hand wash cold if needed.',
        'polyester': 'Machine wash cold, tumble dry low. Wrinkle resistant.',
        'denim': 'Machine wash cold, tumble dry medium. Wash inside out.',
        'leather': 'Spot clean only. Professional cleaning recommended.',
        'linen': 'Machine wash cold, line dry. Iron while damp.',
        'cashmere': 'Hand wash cold or dry clean. Lay flat to dry.'
    }
    
    STYLING_TIPS = {
        'top': {
            'casual': 'Pairs well with jeans or chinos',
            'formal': 'Best with dress pants and blazer',
            'dressy': 'Style with a midi skirt or tailored pants'
        },
        'bottom': {
            'jeans': 'Versatile - dress up or down with different tops',
            'chinos': 'Great for business casual with polo or button-down',
            'skirt': 'Pair with tucked-in blouse or fitted top'
        },
        'dress': {
            'casual': 'Add sneakers for daytime or sandals for summer',
            'formal': 'Complete with heels and statement jewelry',
            'midi': 'Perfect with ankle boots or strappy sandals'
        },
        'outerwear': {
            'jacket': 'Layer over most outfits for instant polish',
            'blazer': 'Elevates casual looks, essential for work',
            'coat': 'Choose based on warmth needs and style preference'
        }
    }
    
    def __init__(self):
        """Initialize the metadata enhancer."""
        logger.info("Fashion Metadata Enhancer initialized")
    
    def enhance_product(
        self,
        product: Dict,
        extract_from_image: bool = False
    ) -> Dict:
        """
        Enhance a product with rich fashion metadata.
        
        Args:
            product: Basic product info (name, category, etc.)
            extract_from_image: Whether to analyze the image
            
        Returns:
            Enhanced product with additional metadata
        """
        enhanced = product.copy()
        
        # Extract style tags
        enhanced['style_tags'] = self._infer_style_tags(product)
        
        # Add occasion suggestions
        enhanced['occasions'] = self._infer_occasions(product, enhanced['style_tags'])
        
        # Add seasonal recommendations
        enhanced['seasons'] = self._infer_seasons(product)
        
        # Add care instructions
        if 'material' in product or 'fabric' in product:
            material = product.get('material') or product.get('fabric')
            enhanced['care_instructions'] = self._get_care_instructions(material)
        
        # Add styling tips
        enhanced['styling_tips'] = self._get_styling_tips(product)
        
        # Add color analysis if image provided
        if extract_from_image and 'image_path' in product:
            color_info = self._analyze_colors(product['image_path'])
            enhanced.update(color_info)
        
        return enhanced
    
    def _infer_style_tags(self, product: Dict) -> List[str]:
        """Infer style tags from product name and description."""
        text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        category = product.get('category', '').lower()
        
        tags = set()
        
        # Check against style categories
        for style, keywords in self.STYLE_CATEGORIES.items():
            if any(keyword in text or keyword in category for keyword in keywords):
                tags.add(style)
        
        # Default to casual if no style found
        if not tags:
            tags.add('casual')
        
        return list(tags)
    
    def _infer_occasions(self, product: Dict, style_tags: List[str]) -> List[str]:
        """Infer suitable occasions based on style."""
        occasions = set()
        
        for occasion, styles in self.OCCASION_MAPPING.items():
            if any(style in style_tags for style in styles):
                occasions.add(occasion)
        
        return list(occasions) if occasions else ['casual']
    
    def _infer_seasons(self, product: Dict) -> List[str]:
        """Infer suitable seasons for the product."""
        text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        category = product.get('category', '').lower()
        
        seasons = set()
        
        for season, keywords in self.SEASON_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                seasons.add(season)
        
        # Default based on category
        if not seasons:
            if any(word in category for word in ['shorts', 'tank', 'sandal']):
                seasons.add('summer')
            elif any(word in category for word in ['coat', 'jacket', 'boot']):
                seasons.update(['fall', 'winter'])
            else:
                seasons.add('all-season')
        
        return list(seasons)
    
    def _get_care_instructions(self, material: str) -> str:
        """Get care instructions based on material."""
        material_lower = material.lower()
        
        for fabric, instructions in self.CARE_INSTRUCTIONS.items():
            if fabric in material_lower:
                return instructions
        
        return "Follow care label instructions. When in doubt, use cold water and gentle cycle."
    
    def _get_styling_tips(self, product: Dict) -> str:
        """Generate styling tips based on category."""
        category = product.get('category', '').lower()
        style_tags = product.get('style_tags', ['casual'])
        
        # Match category
        for cat_type, tips in self.STYLING_TIPS.items():
            if cat_type in category:
                # Get specific tip based on style
                for style in style_tags:
                    if style in tips:
                        return tips[style]
                # Return first tip if no style match
                return next(iter(tips.values()))
        
        return "A versatile piece that can be styled for various occasions."
    
    def _analyze_colors(self, image_path: str) -> Dict:
        """
        Analyze dominant colors in an image.
        Simple implementation without ML.
        """
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((100, 100))  # Reduce size for faster processing
            
            pixels = np.array(img).reshape(-1, 3)
            
            # Simple color categorization
            dominant_colors = []
            
            # Calculate color statistics
            for pixel in pixels[::100]:  # Sample every 100th pixel
                r, g, b = pixel
                
                # Categorize color
                if r > 200 and g > 200 and b > 200:
                    color = 'white'
                elif r < 50 and g < 50 and b < 50:
                    color = 'black'
                elif r > g and r > b:
                    color = 'red'
                elif g > r and g > b:
                    color = 'green'
                elif b > r and b > g:
                    color = 'blue'
                elif r > 150 and g > 150:
                    color = 'yellow'
                elif r > 150 and b > 150:
                    color = 'purple'
                elif g > 150 and b > 150:
                    color = 'cyan'
                else:
                    color = 'neutral'
                
                dominant_colors.append(color)
            
            # Get most common colors
            color_counts = Counter(dominant_colors)
            top_colors = [color for color, _ in color_counts.most_common(3)]
            
            return {
                'dominant_colors': top_colors[:2],
                'color_palette': top_colors
            }
        
        except Exception as e:
            logger.error(f"Error analyzing colors: {e}")
            return {
                'dominant_colors': ['unknown'],
                'color_palette': []
            }
    
    def search_by_criteria(
        self,
        products: List[Dict],
        style: Optional[str] = None,
        occasion: Optional[str] = None,
        season: Optional[str] = None,
        color: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter products by fashion criteria.
        Simple filtering without vector database.
        """
        filtered = products
        
        if style:
            filtered = [p for p in filtered if style in p.get('style_tags', [])]
        
        if occasion:
            filtered = [p for p in filtered if occasion in p.get('occasions', [])]
        
        if season:
            filtered = [p for p in filtered if season in p.get('seasons', [])]
        
        if color:
            filtered = [
                p for p in filtered 
                if color in p.get('dominant_colors', []) or color in p.get('color_palette', [])
            ]
        
        return filtered
    
    def get_outfit_suggestions(
        self,
        item: Dict,
        available_items: List[Dict]
    ) -> List[Dict]:
        """
        Suggest items that go well with the given item.
        Simple rule-based outfit creation.
        """
        category = item.get('category', '').lower()
        style_tags = item.get('style_tags', [])
        occasions = item.get('occasions', [])
        
        # Define complementary categories
        complements = {
            'top': ['bottom', 'shoes', 'outerwear'],
            'bottom': ['top', 'shoes', 'outerwear'],
            'dress': ['shoes', 'outerwear', 'accessories'],
            'shoes': ['top', 'bottom'],
            'outerwear': ['top', 'bottom']
        }
        
        # Find complementary items with matching style/occasion
        suggestions = []
        target_categories = complements.get(category, [])
        
        for available_item in available_items:
            avail_category = available_item.get('category', '').lower()
            avail_style = available_item.get('style_tags', [])
            avail_occasion = available_item.get('occasions', [])
            
            # Check if category complements
            if not any(cat in avail_category for cat in target_categories):
                continue
            
            # Check if style matches
            style_match = any(s in avail_style for s in style_tags)
            occasion_match = any(o in avail_occasion for o in occasions)
            
            if style_match or occasion_match:
                suggestions.append(available_item)
        
        return suggestions[:5]  # Return top 5


# Global instance
_metadata_enhancer = None

def get_fashion_metadata_enhancer() -> FashionMetadataEnhancer:
    """Get or create the metadata enhancer instance."""
    global _metadata_enhancer
    
    if _metadata_enhancer is None:
        _metadata_enhancer = FashionMetadataEnhancer()
    
    return _metadata_enhancer
