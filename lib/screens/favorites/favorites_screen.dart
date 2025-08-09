import 'package:flutter/material.dart';
import 'dart:ui';

class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: backgroundColor.withOpacity(0.8),
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
      body: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 0.7,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
        ),
        itemCount: favoriteItems.length,
        itemBuilder: (context, index) {
          final item = favoriteItems[index];
          return _buildFavoriteItem(item);
        },
      ),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        height: 56,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black.withOpacity(0.8),
              Colors.black.withOpacity(0.6),
            ],
          ),
          borderRadius: BorderRadius.circular(28),
          border: Border.all(
            color: Colors.white.withOpacity(0.1),
            width: 0.5,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(28),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(
                  icon: Icons.home_rounded,
                  isActive: false,
                  onTap: () => Navigator.pop(context),
                ),
                _buildNavItem(
                  icon: Icons.favorite,
                  isActive: true,
                  onTap: () {},
                ),
                _buildScannerButton(),
                _buildNavItem(
                  icon: Icons.shopping_bag_outlined,
                  isActive: false,
                  onTap: () {},
                ),
                _buildNavItem(
                  icon: Icons.person_outline,
                  isActive: false,
                  onTap: () {},
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required IconData icon,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: isActive 
            ? const Color(0xFF06F81A) 
            : Colors.transparent,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Icon(
          icon,
          color: isActive 
            ? Colors.black
            : Colors.white.withOpacity(0.7),
          size: 24,
        ),
      ),
    );
  }

  Widget _buildScannerButton() {
    return Container(
      width: 56,
      height: 56,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF06F81A),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF06F81A).withOpacity(0.3),
            blurRadius: 12,
            spreadRadius: 2,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: const Icon(
        Icons.qr_code_scanner,
        color: Colors.black,
        size: 28,
      ),
    );
  }

  Widget _buildFavoriteItem(FavoriteItem item) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
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
                ),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.favorite,
                    color: Color(0xFF06F81A),
                    size: 20,
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
    );
  }
}

class FavoriteItem {
  final String name;
  final double price;
  final String imageUrl;

  const FavoriteItem({
    required this.name,
    required this.price,
    required this.imageUrl,
  });
}

final List<FavoriteItem> favoriteItems = [
  FavoriteItem(
    name: 'Cyber Goth Jacket',
    price: 250.00,
    imageUrl: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?q=80&w=735&auto=format&fit=crop',
  ),
  FavoriteItem(
    name: 'Techwear Pants',
    price: 180.00,
    imageUrl: 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?q=80&w=687&auto=format&fit=crop',
  ),
  FavoriteItem(
    name: 'Holographic Top',
    price: 95.00,
    imageUrl: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=662&auto=format&fit=crop',
  ),
  FavoriteItem(
    name: 'LED Sneakers',
    price: 320.00,
    imageUrl: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1470&auto=format&fit=crop',
  ),
  FavoriteItem(
    name: 'Reflective Jacket',
    price: 150.00,
    imageUrl: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=736&auto=format&fit=crop',
  ),
  FavoriteItem(
    name: 'Designer Shades',
    price: 80.00,
    imageUrl: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=880&auto=format&fit=crop',
  ),
];