import 'package:flutter/material.dart';
import 'dart:ui';
import '../../widgets/bottom_navigation_bar.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  final List<CartItem> cartItems = [
    CartItem(
      name: 'Cyberpunk Jacket',
      size: 'M',
      price: 250.00,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtwM4L2kjjsx_HS96IW7kfoMSbozy47HKGs4jiPjGVCmadqqkqoRzyTtKJp_40DyoeZdfc83f0TWCF33e8hU017t9vw3yghq_ChqywkHtObE9Bnv9qIfd9BYsrZ-JpX7fO9HBf295TOt1AUvuHFUF21TaxEnZUVS91-V9Mf7WqD9HFQaCmHGwy3NGuxSkqPjnY9WG8thRIr4w8mbm9KA9yZ1UFgyQWKmHH5m4jV-vKj23VDFbqwRXWoCiNs_EulOLxxGRW-KZ9tzKA',
      quantity: 1,
    ),
    CartItem(
      name: 'Neon Tee',
      size: 'L',
      price: 75.00,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBFpi2riJdl2bADr4mKoPMUbuZqm2gH_zIv41LUx5NQb71oTf9XSUkPfpY7XDIMv6TPDrXHf3hl0gdNsu5n7liQcDU2wwl5pSGpoFRQPl61RP_u0kKJSIKDl-CctAH9qAFX8XNe0fTHtKP25oLLZyfvGDC6a5fWY4niTcifgi8I6lbUjpolKz1CEo-PHFXYBuChtKAFZOpy_cNhtcw1g8qsL3sYXGCOhJPWJ7J75U50HJqk7eqlJlt9hwsRVzneJvYi4LuemZPIvVT3',
      quantity: 2,
    ),
  ];

  double get subtotal => cartItems.fold(
      0, (sum, item) => sum + (item.price * item.quantity));
  double get shipping => 10.00;
  double get total => subtotal + shipping;

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);
    const textSecondary = Color(0xFFA0A0A0);

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
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
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
                        child: Image.network(
                          item.imageUrl,
                          width: 96,
                          height: 96,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.name,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                                fontSize: 16,
                              ),
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
                          _buildQuantityButton(
                            icon: Icons.remove,
                            onPressed: () => _updateQuantity(index, -1),
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8),
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
                            onPressed: () => _updateQuantity(index, 1),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
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
                  _buildPriceRow('Subtotal', subtotal),
                  const SizedBox(height: 8),
                  _buildPriceRow('Shipping', shipping),
                  const SizedBox(height: 8),
                  _buildPriceRow('Total', total, isTotal: true),
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

  void _updateQuantity(int index, int change) {
    setState(() {
      final newQuantity = cartItems[index].quantity + change;
      if (newQuantity > 0) {
        cartItems[index].quantity = newQuantity;
      }
    });
  }


}

class CartItem {
  final String name;
  final String size;
  final double price;
  final String imageUrl;
  int quantity;

  CartItem({
    required this.name,
    required this.size,
    required this.price,
    required this.imageUrl,
    required this.quantity,
  });
}