import 'package:flutter/material.dart';
import '../product/product_detail_screen.dart';
import '../../widgets/chat_fab_overlay.dart';
import '../../data/products_data.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  String selectedCategory = 'All';
  final TextEditingController _searchController = TextEditingController(text: 'Clothing');

  final List<String> categories = ['All', 'Men', 'Women'];
  
  List<ProductItem> get products => allProducts;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const darkGreenBg = Color(0xFF0A140A);
    const primaryColor = Color(0xFF06f906);
    const inputBg = Color(0xFF1A291A);
    const textMuted = Color(0xFF9ca3af);
    const borderColor = Color(0xFF3f3f46);
    const textPrimary = Color(0xFFFFFFFF);

    return Scaffold(
      backgroundColor: darkGreenBg,
      body: Stack(
        children: [
          SafeArea(
            child: Column(
              children: [
                // Header
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(
                      Icons.arrow_back,
                      color: textPrimary,
                      size: 24,
                    ),
                  ),
                  Expanded(
                    child: Text(
                      'Search',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: textPrimary,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                  ),
                  const SizedBox(width: 48), // Balance the header
                ],
              ),
            ),
            
            // Search Input
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Container(
                decoration: BoxDecoration(
                  color: inputBg,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(left: 12),
                      child: Icon(
                        Icons.search,
                        color: textMuted,
                        size: 20,
                      ),
                    ),
                    Expanded(
                      child: TextField(
                        controller: _searchController,
                        style: const TextStyle(
                          color: textPrimary,
                          fontSize: 16,
                        ),
                        decoration: const InputDecoration(
                          hintText: 'Search for clothing...',
                          hintStyle: TextStyle(color: textMuted),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 16,
                          ),
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        _searchController.clear();
                      },
                      icon: const Icon(
                        Icons.close,
                        color: textMuted,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Filters and Sort
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      border: Border.all(color: borderColor),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.tune,
                          color: textPrimary,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Filters',
                          style: TextStyle(
                            color: textPrimary,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      border: Border.all(color: borderColor),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.sort,
                          color: textPrimary,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Sort',
                          style: TextStyle(
                            color: textPrimary,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Categories
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: borderColor),
                ),
              ),
              child: Row(
                children: categories.map((category) {
                  final isSelected = selectedCategory == category;
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        selectedCategory = category;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
                      decoration: BoxDecoration(
                        border: Border(
                          bottom: BorderSide(
                            color: isSelected ? primaryColor : Colors.transparent,
                            width: 2,
                          ),
                        ),
                      ),
                      child: Text(
                        category,
                        style: TextStyle(
                          color: isSelected ? primaryColor : textMuted,
                          fontSize: 14,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Products Grid
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 0.75,
                  ),
                  itemCount: products.length,
                  itemBuilder: (context, index) {
                    final product = products[index];
                    return _buildProductCard(product);
                  },
                ),
              ),
            ),
              ],
            ),
          ),
          const ChatFabOverlay(),
        ],
      ),
    );
  }

  Widget _buildProductCard(ProductItem product) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailScreen(
              product: product,
              productImages: [product.imageUrl],
            ),
          ),
        );
      },
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFF1A291A),
                borderRadius: BorderRadius.circular(8),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: product.imageUrl.startsWith('http')
                    ? Image.network(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Center(
                            child: CircularProgressIndicator(
                              color: const Color(0xFF06f906),
                              value: loadingProgress.expectedTotalBytes != null
                                  ? loadingProgress.cumulativeBytesLoaded /
                                      loadingProgress.expectedTotalBytes!
                                  : null,
                            ),
                          );
                        },
                      )
                    : Image.asset(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const Center(
                          child: Icon(Icons.image_not_supported, color: Color(0xFF06f906), size: 40),
                        ),
                      ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            product.name,
            style: const TextStyle(
              color: Color(0xFFFFFFFF),
              fontSize: 14,
              fontWeight: FontWeight.w500,
              fontFamily: 'SpaceGrotesk',
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            '₹${product.price.toStringAsFixed(2)}',
            style: const TextStyle(
              color: Color(0xFF06f906),
              fontSize: 14,
              fontWeight: FontWeight.bold,
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ],
      ),
    );
  }
}


