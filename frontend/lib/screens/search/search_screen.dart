import 'package:flutter/material.dart';
import '../product/product_detail_screen.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  String selectedCategory = 'All';
  final TextEditingController _searchController = TextEditingController(text: 'Clothing');

  final List<String> categories = ['All', 'Men', 'Women'];
  
  final List<ProductItem> products = [
    ProductItem(
      name: 'Flowy Summer Dress',
      price: 49.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAfo527qrKlgw7yTKR4jBJnJaKttmLid9gnoiBaxjWES0fa9zhU6QXJrqhp4FpmrBVthSI10HnqWVsFjk_yrUMkH9gKop-xdOrf-1k8BOa89PUgjwfcshLxien-JAjr--EFDmIMoPKAImObL7O_6_1WSDnMsrjMHaeK_qbLFS_fo1wDcvLbjWgs-5M2xpg2nV2DmPthOJCO5QQBdj4rw7LQ6g7YIF-doGpL3KbCwrC_qIt-M_-KAmAR8Vk8LMsXPLOpfWRWHEkXV_SN',
    ),
    ProductItem(
      name: 'Classic Denim Jacket',
      price: 79.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAVUM1j53lJxtcVrAnfU7E1fxsekFLz9wbm6uErCJwswWpbydcN2CAdB2XqSnkcYp7xb4AKE_9r8pLGsqm8jLrCVZNh1pUGYR67OednD9AhotEOa3k_AOTw4ojQhY8Db7SU8MKUJILSu0DYbtOlmU9rICf36kL1jYX6JAoZ6cTlpTyTaAHNYplrK9W1SSGyUcpMncemnSrKkFWSU0Gg5GlWTzlCbNUkUAQdhqI2XJz_KjpCaNtD2CEHH_9cuAs0R8mRBF5waWbJxSQp',
    ),
    ProductItem(
      name: 'High-Waisted Jeans',
      price: 69.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC2Bh_DSKJqHNlh9BQ5QYlt_6pZB-oDbT735kQrlkmn_M5ikem5IPBM6PsH2RhEBcWwxq5TT-vleUNTO7m4MywbY9vHgEp5RBj3FcU-nrkIAnixsER9_e-0q21TgKrcHwzdsGpSDcTuGK0u-na_9P78X0JyEbxUjaQv7xzB-zwJZIVjtWZ9Ck2CQYJedBG2OUIu_IoTjMh8Yb0MCGRNBFrakv1LPOCdnZXfSFdybq0rW_5kb_CiOcv8VShJ7KTlQeDgGBIDBHGYg8yX',
    ),
    ProductItem(
      name: 'Silk Blouse',
      price: 59.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDoDn9EoFeew3O6YPaWCBSjcA9ZFwG9dWtbmCRcTyvXzICShRiVLSib8npXClBcBZ-j9HSQvvwsqE_IfWgYn1WOfkYUF-heVxoJHuL_MdLGw2tKqn5H5Q0eeqD-nWlsKlbB6kIgqcmRXkaaEKbhd5XZYxQAbJGSfPoNzH2P9bq94OB7j87WYA_wQ1cQGkWbcPjgwcGjgl1hoik09tOfqbC6sIohY4wO3YbkI7caRmffQ_sDJlu6ikssomARHIamqwsN06VequiZd5lT',
    ),
    ProductItem(
      name: 'Leather Skirt',
      price: 89.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuApjodMAioxRWhGkCRdtsMuHiMOH-GH6kBidLllL4jaOi0V5FozqXEro35gAr9-hZS5r2B_gPwu1n0u_SlNCwh7p7mRyejpK0EXFH0riD51P0ylCr1aVtkulzO6VmaFZSgaQe1Z16zf2XPum2VoOflm5SVTIa-B8dYIU2M3vzArdS30a6yfgRUPGFnXioz2oLkBEd4hOgq5CQI7NUjanm6K6IzFZitu03Gp87hHEV7-M8q2xPYr4ABWNPnuN3oIgkIAWykyxwPyvCXl',
    ),
    ProductItem(
      name: 'Cashmere Sweater',
      price: 129.99,
      imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD7VcMNO8hTijuB88n_Qy_TxgvlhFqT5w7S5Hu9gHFcgsnQG4g8_p8FxbkX-3PoWYGRChLA8TAe_1KxJe-LddxpBinzC3Gp-LMrjZOAABEnNnYCAtwmDyri0kZPVAElDIUwawqeH-co1sc-KfCNxF9kOmAp9bZnZBfWMdjHYyQauzWEm1tAVtbvot36LhOxHHxvomjNhJxRghY6P4Dqvbfz8gMF4BBzPMnaAJ1IjduQCwV-Jj67b_IVRaGemiPIgEu3HfXFm8on6bSb',
    ),
  ];

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
      body: SafeArea(
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
    );
  }

  Widget _buildProductCard(ProductItem product) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailScreen(product: product),
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
                child: Image.network(
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


