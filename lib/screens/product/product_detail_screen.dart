import 'package:flutter/material.dart';

class ProductDetailScreen extends StatefulWidget {
  final ProductItem product;
  
  const ProductDetailScreen({
    super.key,
    required this.product,
  });

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  String selectedSize = 'S';
  String selectedColor = 'Black';
  int quantity = 1;
  
  final List<String> sizes = ['XS', 'S', 'M', 'L'];
  final List<Map<String, dynamic>> colors = [
    {'name': 'Black', 'color': Colors.black},
    {'name': 'White', 'color': Colors.white},
    {'name': 'Gray', 'color': Colors.grey},
  ];

  final List<String> productImages = [
    'https://lh3.googleusercontent.com/aida-public/AB6AXuBqvJZ3YlnbQjhhX1HYEI0I3GFzEY3b7ATOMYKB7SlzXSqg8FKsKGzvq0N0NOj9WRGDvSTEhz-USPOh_XUr0ZhOSV8TRd3qiKq-xvVuG1hw6wUJ9pVvJM3kr7b8NntIIkBwIYcPxrlMR4Z1reQgWFgswj3UcyiCFehG5mEvQPetRF4qzOlZ33Ga9bQ060ZVoYGpkTRaxrR1xCB1wXqWEAFvMSWH29hAx6VjaayJqZ7ub1CWrjc4CUAlfoy0Wx7eXDofu0tZjdC4iw5g',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuCtDtg6qNUHdw7m3Pu8fzxpCgIMHIwpFHOUZHBDLANlkSYPpHGhpoqRJKLaAsAm8iJR2NAac6uuIjsvACEKF-KPbeGe0sUfnAVqKyfbte306wlnoNIXMZsllGEbDAHq8-wKC8j3e8JTnNNoP5RMY7sLNQ_DvXc02d1H9RhmOCgJxFdoUREr66S8G76_ry9SOLooUYM2GEjD7dotA9od8Tg31dux2VsqMmvwT7J0mRBWwzBPo3DQ3kO7FK5UEtF3r8fqZJqO_re2gRXd',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuDB_oc_xQcD5Uu448QUY3RZOEOd9Ua16S_OGWRymk3QokS7BI6xp26d0uZnAiK96sLS6iCC7zLZnZWR4hua1W125ihSDOVGNEBmh9KyqtjH6Cq4Z6E-YfMD2_0iwjvSZWaLi_0dFH1OMKI2kXXXu1cnsJo_uurfOyFvAmVJD7OnWv1QP-2zE1s-ANCWVIwCUY8iT30UJoZt4yWSXIoXL5dVlR3eexECFxUOZ8MDXPJj06SSUt3Xn4Xsgwr9O-zYFfq3oBU_NShRi3-L',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuAfo527qrKlgw7yTKR4jBJnJaKttmLid9gnoiBaxjWES0fa9zhU6QXJrqhp4FpmrBVthSI10HnqWVsFjk_yrUMkH9gKop-xdOrf-1k8BOa89PUgjwfcshLxien-JAjr--EFDmIMoPKAImObL7O_6_1WSDnMsrjMHaeK_qbLFS_fo1wDcvLbjWgs-5M2xpg2nV2DmPthOJCO5QQBdj4rw7LQ6g7YIF-doGpL3KbCwrC_qIt-M_-KAmAR8Vk8LMsXPLOpfWRWHEkXV_SN',
  ];

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const secondaryBg = Color(0xFF1E1E1E);
    const primaryColor = Color(0xFF3DDC84);
    const accentSecondary = Color(0xFF2A2A2A);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);

    return Scaffold(
      backgroundColor: backgroundColor,
      body: Column(
        children: [
          // Header with back and favorites buttons
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(
                      Icons.arrow_back,
                      color: textPrimary,
                      size: 20,
                    ),
                  ),
                ),
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: IconButton(
                    onPressed: () {
                      // TODO: Add to favorites
                    },
                    icon: const Icon(
                      Icons.favorite_border,
                      color: textPrimary,
                      size: 20,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Image Gallery
          SizedBox(
            height: 400,
            child: PageView.builder(
              itemCount: productImages.length,
              itemBuilder: (context, index) {
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.network(
                      productImages[index],
                      fit: BoxFit.cover,
                      width: double.infinity,
                      loadingBuilder: (context, child, loadingProgress) {
                        if (loadingProgress == null) return child;
                        return Center(
                          child: CircularProgressIndicator(
                            color: primaryColor,
                            value: loadingProgress.expectedTotalBytes != null
                                ? loadingProgress.cumulativeBytesLoaded /
                                    loadingProgress.expectedTotalBytes!
                                : null,
                          ),
                        );
                      },
                    ),
                  ),
                );
              },
            ),
          ),

          // Product Info Section
          Expanded(
            child: Transform.translate(
              offset: const Offset(0, -24),
              child: Container(
                decoration: const BoxDecoration(
                  color: secondaryBg,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(24),
                    topRight: Radius.circular(24),
                  ),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Product Title and Price
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  widget.product.name,
                                  style: const TextStyle(
                                    color: textPrimary,
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Evening Wear',
                                  style: TextStyle(
                                    color: textSecondary,
                                    fontSize: 16,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            '₹${widget.product.price.toStringAsFixed(2)}',
                            style: TextStyle(
                              color: primaryColor,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 24),

                      // Size Selection
                      const Text(
                        'Size',
                        style: TextStyle(
                          color: textPrimary,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'SpaceGrotesk',
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: sizes.map((size) {
                          final isSelected = selectedSize == size;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedSize = size;
                              });
                            },
                            child: Container(
                              height: 40,
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              margin: const EdgeInsets.only(right: 12),
                              decoration: BoxDecoration(
                                color: isSelected ? primaryColor : accentSecondary,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Center(
                                child: Text(
                                  size,
                                  style: TextStyle(
                                    color: isSelected ? Colors.black : textPrimary,
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 24),

                      // Color Selection
                      const Text(
                        'Color',
                        style: TextStyle(
                          color: textPrimary,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'SpaceGrotesk',
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: colors.map((colorData) {
                          final isSelected = selectedColor == colorData['name'];
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedColor = colorData['name'];
                              });
                            },
                            child: Container(
                              margin: const EdgeInsets.only(right: 16),
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: colorData['color'],
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: isSelected ? primaryColor : Colors.transparent,
                                  width: 3,
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 24),

                      // Description
                      const Text(
                        'Description',
                        style: TextStyle(
                          color: textPrimary,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'SpaceGrotesk',
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'A stunning black dress perfect for evening events. Features a flattering silhouette and high-quality fabric that drapes beautifully. This is your go-to for a night of elegance.',
                        style: TextStyle(
                          color: textSecondary,
                          fontSize: 16,
                          height: 1.5,
                          fontFamily: 'SpaceGrotesk',
                        ),
                      ),

                      const SizedBox(height: 24),

                      // Reviews
                      const Text(
                        'Reviews (120)',
                        style: TextStyle(
                          color: textPrimary,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'SpaceGrotesk',
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          // Rating
                          Column(
                            children: [
                              const Text(
                                '4.5',
                                style: TextStyle(
                                  color: textPrimary,
                                  fontSize: 32,
                                  fontWeight: FontWeight.w900,
                                  fontFamily: 'SpaceGrotesk',
                                ),
                              ),
                              Row(
                                children: List.generate(5, (index) {
                                  return Icon(
                                    Icons.star,
                                    color: index < 4 ? primaryColor : Colors.grey[600],
                                    size: 16,
                                  );
                                }),
                              ),
                            ],
                          ),
                          const SizedBox(width: 16),
                          // Rating bars
                          Expanded(
                            child: Column(
                              children: [
                                _buildRatingBar(5, 0.4),
                                _buildRatingBar(4, 0.3),
                                _buildRatingBar(3, 0.15),
                                _buildRatingBar(2, 0.1),
                                _buildRatingBar(1, 0.05),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 32),

                      // Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: Container(
                              height: 56,
                              decoration: BoxDecoration(
                                color: accentSecondary,
                                borderRadius: BorderRadius.circular(28),
                              ),
                              child: const Center(
                                child: Text(
                                  'Try On',
                                  style: TextStyle(
                                    color: textPrimary,
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Container(
                              height: 56,
                              decoration: BoxDecoration(
                                color: primaryColor,
                                borderRadius: BorderRadius.circular(28),
                              ),
                              child: const Center(
                                child: Text(
                                  'Add to Cart',
                                  style: TextStyle(
                                    color: Colors.black,
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRatingBar(int rating, double percentage) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 20,
            child: Text(
              '$rating',
              style: const TextStyle(
                color: Color(0xFFA0A0A0),
                fontSize: 12,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Container(
              height: 6,
              decoration: BoxDecoration(
                color: const Color(0xFF2A2A2A),
                borderRadius: BorderRadius.circular(3),
              ),
              child: FractionallySizedBox(
                alignment: Alignment.centerLeft,
                widthFactor: percentage,
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF3DDC84),
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ProductItem {
  final String name;
  final double price;
  final String imageUrl;

  const ProductItem({
    required this.name,
    required this.price,
    required this.imageUrl,
  });
}
