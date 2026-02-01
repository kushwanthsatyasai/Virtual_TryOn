import 'package:flutter/material.dart';
import 'dart:ui';
import '../product/product_detail_screen.dart'; // ProductItem
import '../../widgets/bottom_navigation_bar.dart';
import '../../widgets/chat_fab_overlay.dart';
import '../../services/favorites_cart_store.dart';

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    final items = FavoritesCartStore.favorites;

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: backgroundColor.withValues(alpha: 0.8),
        title: const Text(
          'Favorites',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            letterSpacing: -1,
            color: Colors.white,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
      ),
      body: Stack(
        children: [
          items.isEmpty
              ? const Center(
                  child: Text(
                    'No favorites yet.\nAdd items from product details.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xFFA0A0A0),
                      fontSize: 16,
                      fontFamily: 'SpaceGrotesk',
                    ),
                  ),
                )
              : GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 0.7,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                  ),
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return _buildFavoriteItem(item, index);
                  },
                ),
          const ChatFabOverlay(),
        ],
      ),
      bottomNavigationBar: const CustomBottomNavigationBar(
        currentIndex: 1,
      ),
    );
  }

  Widget _buildFavoriteItem(FavoriteItem item, int index) {
    return GestureDetector(
      onTap: () {
        final product = ProductItem(
          name: item.name,
          price: item.price,
          imageUrl: item.imageUrl,
        );
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailScreen(
              product: product,
              productImages: [item.imageUrl],
            ),
          ),
        ).then((_) => setState(() {}));
      },
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: item.imageUrl.startsWith('http')
                      ? Image.network(
                          item.imageUrl,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          loadingBuilder: (context, child, loadingProgress) {
                            if (loadingProgress == null) return child;
                            return Center(
                              child: CircularProgressIndicator(
                                color: const Color(0xFF06F81A),
                                value: loadingProgress.expectedTotalBytes != null
                                    ? loadingProgress.cumulativeBytesLoaded /
                                        loadingProgress.expectedTotalBytes!
                                    : null,
                              ),
                            );
                          },
                          errorBuilder: (_, __, ___) => Container(
                            color: const Color(0xFF1E1E1E),
                            child: const Icon(
                              Icons.image_not_supported,
                              color: Color(0xFFA0A0A0),
                              size: 40,
                            ),
                          ),
                        )
                      : Image.asset(
                          item.imageUrl,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            color: const Color(0xFF1E1E1E),
                            child: const Icon(
                              Icons.image_not_supported,
                              color: Color(0xFFA0A0A0),
                              size: 40,
                            ),
                          ),
                        ),
                ),
                Positioned(
                  top: 8,
                  right: 8,
                  child: GestureDetector(
                    onTap: () {
                      FavoritesCartStore.removeFavoriteAt(index);
                      setState(() {});
                    },
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.5),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.favorite,
                        color: Color(0xFF06F81A),
                        size: 20,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            item.name,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w600,
              fontFamily: 'SpaceGrotesk',
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            '₹${item.price.toStringAsFixed(2)}',
            style: const TextStyle(
              color: Color(0xFFA0A0A0),
              fontSize: 14,
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ],
      ),
    );
  }
}
