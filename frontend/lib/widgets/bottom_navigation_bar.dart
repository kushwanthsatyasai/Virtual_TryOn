import 'package:flutter/material.dart';
import 'dart:ui';
import '../screens/home/home_screen.dart';
import '../screens/favorites/favorites_screen.dart';
import '../screens/cart/cart_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/qr/qr_screen.dart';

class CustomBottomNavigationBar extends StatelessWidget {
  final int currentIndex;

  const CustomBottomNavigationBar({
    super.key,
    required this.currentIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      height: 80,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.black.withValues(alpha: 0.8),
            Colors.black.withValues(alpha: 0.6),
          ],
        ),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
          width: 0.5,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(
                  icon: Icons.home_rounded,
                  isActive: currentIndex == 0,
                  onTap: () => _navigateToScreen(0, context),
                ),
                _buildNavItem(
                  icon: Icons.favorite_outline,
                  isActive: currentIndex == 1,
                  onTap: () => _navigateToScreen(1, context),
                ),
                _buildScannerButton(context),
                _buildNavItem(
                  icon: Icons.shopping_bag_outlined,
                  isActive: currentIndex == 2,
                  onTap: () => _navigateToScreen(2, context),
                ),
                _buildNavItem(
                  icon: Icons.person_outline,
                  isActive: currentIndex == 3,
                  onTap: () => _navigateToScreen(3, context),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _navigateToScreen(int index, BuildContext context) {
    // Don't navigate if we're already on the current screen
    if (index == currentIndex) return;

    Widget targetScreen;
    switch (index) {
      case 0:
        targetScreen = const HomeScreen();
        break;
      case 1:
        targetScreen = const FavoritesScreen();
        break;
      case 2:
        targetScreen = const CartScreen();
        break;
      case 3:
        targetScreen = const ProfileScreen();
        break;
      default:
        return;
    }

    // Use pushReplacement to avoid stack buildup
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => targetScreen),
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
        width: 56,
        height: 56,
        decoration: BoxDecoration(
          color: isActive 
            ? const Color(0xFF06F81A) 
            : Colors.transparent,
          borderRadius: BorderRadius.circular(28),
        ),
        child: Icon(
          icon,
          color: isActive 
            ? Colors.black
            : const Color(0xFFA0A0A0),
          size: 24,
        ),
      ),
    );
  }

  Widget _buildScannerButton(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const QRScreen()),
        );
      },
      child: Transform.translate(
        offset: const Offset(0, -8),
        child: Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: const Color(0xFF06F81A),
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF06F81A).withValues(alpha: 0.3),
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
      ),
    );
  }
}
