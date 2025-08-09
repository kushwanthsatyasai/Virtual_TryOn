import 'package:flutter/material.dart';
import 'dart:ui';
import '../cart/cart_screen.dart';
import '../profile/profile_screen.dart';
import '../favorites/favorites_screen.dart';
import '../qr/qr_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  Widget build(BuildContext context) {
    // Colors from design
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);
    const navBackground = Color(0xFF1A1A1A);

    return Scaffold(
      backgroundColor: backgroundColor,
      // App Bar
      appBar: AppBar(
        backgroundColor: backgroundColor.withOpacity(0.8),
        flexibleSpace: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(color: Colors.transparent),
          ),
        ),
        title: const Text(
          'VIRTUE',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            letterSpacing: -1,
            color: textPrimary,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search, color: textPrimary),
            onPressed: () {
              // TODO: Implement search
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      
      // Body
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Recent Looks Section
            _buildSection(
              'Recent Looks',
              [
                _buildLookCard('Street Style', 'assets/images/street_style.png'),
                _buildLookCard('Casual Vibes', 'assets/images/casual_vibes.png'),
                _buildLookCard('Evening Elegance', 'assets/images/evening_elegance.png'),
              ],
            ),
            
            // Trending Section
            _buildSection(
              'Trending',
              [
                _buildLookCard('Urban Chic', 'assets/images/urban_chic.png'),
                _buildLookCard('Modern Edge', 'assets/images/modern_edge.png'),
                _buildLookCard('Sophisticated Style', 'assets/images/sophisticated_style.png'),
              ],
            ),
          ],
        ),
      ),

      // Bottom Navigation Bar
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
                  label: 'Home',
                  isActive: true,
                  onTap: () {},
                ),
                _buildNavItem(
                  icon: Icons.favorite_outline,
                  label: 'Favorites',
                  isActive: false,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const FavoritesScreen()),
                    );
                  },
                ),
                _buildScannerButton(),
                _buildNavItem(
                  icon: Icons.shopping_bag_outlined,
                  label: 'Cart',
                  isActive: false,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const CartScreen()),
                    );
                  },
                ),
                _buildNavItem(
                  icon: Icons.person_outline,
                  label: 'Profile',
                  isActive: false,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const ProfileScreen()),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFFFFFFF),
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ),
        SizedBox(
          height: 280,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: items.map((item) => Padding(
              padding: const EdgeInsets.only(right: 16),
              child: item,
            )).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildLookCard(String title, String imageUrl) {
    return SizedBox(
      width: 176,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: AspectRatio(
              aspectRatio: 3/4,
              child: Image.asset(
                imageUrl,
                fit: BoxFit.cover,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: const TextStyle(
              color: Color(0xFFA0A0A0),
              fontSize: 14,
              fontWeight: FontWeight.w500,
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ],
      ),
    );
  }

  // Update the _buildNavItem method:
  Widget _buildNavItem({
    required IconData icon,
    required String label,
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
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const QRScreen()),
        );
      },
      child: Container(
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
      ),
    );
  }
}