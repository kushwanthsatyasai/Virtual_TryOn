import 'package:flutter/material.dart';
import '../../widgets/bottom_navigation_bar.dart';
import '../../widgets/chat_fab_overlay.dart';
import '../../services/favorites_cart_store.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  double get _subtotal {
    final items = FavoritesCartStore.cartItems;
    return items.fold(0.0, (sum, item) => sum + (item.price * item.quantity));
  }

  double get _shipping => 10.00;
  double get _total => _subtotal + _shipping;

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);
    const textSecondary = Color(0xFFA0A0A0);
    final cartItems = FavoritesCartStore.cartItems;

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: backgroundColor,
        title: const Text(
          'My Cart',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            letterSpacing: -1,
            color: Colors.white,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          Column(
            children: [
              Expanded(
                child: cartItems.isEmpty
                    ? const Center(
                        child: Text(
                          'Your cart is empty.\nAdd items from product details.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFA0A0A0),
                            fontSize: 16,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: cartItems.length,
                        itemBuilder: (context, index) {
                          final item = cartItems[index];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 16),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: cardBackground,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Row(
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: SizedBox(
                                    width: 96,
                                    height: 96,
                                    child: item.imageUrl.startsWith('http')
                                        ? Image.network(
                                            item.imageUrl,
                                            fit: BoxFit.cover,
                                            errorBuilder: (_, __, ___) =>
                                                const Icon(
                                                    Icons.image_not_supported,
                                                    color: Color(0xFFA0A0A0)),
                                          )
                                        : Image.asset(
                                            item.imageUrl,
                                            fit: BoxFit.cover,
                                            errorBuilder: (_, __, ___) =>
                                                const Icon(
                                                    Icons.image_not_supported,
                                                    color: Color(0xFFA0A0A0)),
                                          ),
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item.name,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: Colors.white,
                                          fontSize: 16,
                                        ),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        'Size: ${item.size}',
                                        style: TextStyle(
                                          color: textSecondary,
                                          fontSize: 14,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        '₹${item.price.toStringAsFixed(2)}',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: primaryColor,
                                          fontSize: 16,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                Column(
                                  children: [
                                    IconButton(
                                      onPressed: () {
                                        FavoritesCartStore.removeCartItemAt(
                                            index);
                                        setState(() {});
                                      },
                                      icon: const Icon(Icons.close,
                                          color: Color(0xFFA0A0A0), size: 20),
                                      padding: EdgeInsets.zero,
                                      constraints: const BoxConstraints(
                                          minWidth: 32, minHeight: 32),
                                    ),
                                    _buildQuantityButton(
                                      icon: Icons.remove,
                                      onPressed: () {
                                        FavoritesCartStore.updateCartQuantity(
                                            index, -1);
                                        setState(() {});
                                      },
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 8),
                                      child: Text(
                                        '${item.quantity}',
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 16,
                                        ),
                                      ),
                                    ),
                                    _buildQuantityButton(
                                      icon: Icons.add,
                                      onPressed: () {
                                        FavoritesCartStore.updateCartQuantity(
                                            index, 1);
                                        setState(() {});
                                      },
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          );
                        },
                      ),
              ),
              if (cartItems.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: backgroundColor,
                    border: Border(
                      top: BorderSide(
                        color: Colors.grey.shade800,
                        width: 1,
                      ),
                    ),
                  ),
                  child: SafeArea(
                    child: Column(
                      children: [
                        _buildPriceRow('Subtotal', _subtotal),
                        const SizedBox(height: 8),
                        _buildPriceRow('Shipping', _shipping),
                        const SizedBox(height: 8),
                        _buildPriceRow('Total', _total, isTotal: true),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          height: 56,
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: primaryColor,
                              foregroundColor: Colors.black,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(28),
                              ),
                            ),
                            onPressed: () {
                              // TODO: Implement checkout
                            },
                            child: const Text(
                              'Checkout',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
          const ChatFabOverlay(),
        ],
      ),
      bottomNavigationBar: const CustomBottomNavigationBar(
        currentIndex: 2,
      ),
    );
  }

  Widget _buildQuantityButton({
    required IconData icon,
    required VoidCallback onPressed,
  }) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: Colors.grey.shade800,
        shape: BoxShape.circle,
      ),
      child: IconButton(
        padding: EdgeInsets.zero,
        icon: Icon(icon, size: 16),
        color: Colors.white,
        onPressed: onPressed,
      ),
    );
  }

  Widget _buildPriceRow(String label, double amount, {bool isTotal = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            color: isTotal ? Colors.white : const Color(0xFFA0A0A0),
            fontSize: isTotal ? 18 : 16,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        Text(
          '₹${amount.toStringAsFixed(2)}',
          style: TextStyle(
            color: isTotal ? const Color(0xFF06F81A) : Colors.white,
            fontSize: isTotal ? 18 : 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
