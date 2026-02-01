import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';

import '../../widgets/chat_fab_overlay.dart';
import '../../services/favorites_cart_store.dart';
import '../../services/try_on_api.dart';
import '../../services/profile_api.dart';
import '../../services/size_recommendation_api.dart';
import '../../services/api_client.dart';

class ProductDetailScreen extends StatefulWidget {
  final ProductItem product;
  /// When set, the gallery shows this (your tried-on look) first; swipe to see product images.
  final String? triedLookImageUrl;
  /// When opening from a recent look, pass product image(s) so swipe shows original product.
  final List<String>? productImages;

  const ProductDetailScreen({
    super.key,
    required this.product,
    this.triedLookImageUrl,
    this.productImages,
  });

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  String selectedSize = 'S';
  String selectedColor = 'Black';
  int quantity = 1;
  bool _addedToCart = false;
  bool _tryOnLoading = false;
  String? _aiRecommendedSize;
  bool _sizeRecommendationLoading = false;

  bool get _isFavorite =>
      FavoritesCartStore.isFavorite(widget.product.name, widget.product.imageUrl);

  final List<String> sizes = ['XS', 'S', 'M', 'L'];
  static const List<String> _shirtKeywords = ['shirt', 't-shirt', 'tshirt', 'blazer', 'sweater', 'hoodie', 'top'];
  static const List<String> _jacketKeywords = ['jacket', 'coat', 'blazer'];
  static const List<String> _pantsKeywords = ['jeans', 'pants', 'skirt', 'trousers'];

  String _garmentTypeFromProductName(String name) {
    final lower = name.toLowerCase();
    if (_pantsKeywords.any(lower.contains)) return 'pants';
    if (_jacketKeywords.any(lower.contains)) return 'jacket';
    if (_shirtKeywords.any(lower.contains)) return 'shirt';
    return 'shirt';
  }

  Future<void> _fetchSizeRecommendation() async {
    if (_sizeRecommendationLoading) return;
    setState(() => _sizeRecommendationLoading = true);
    try {
      final result = await SizeRecommendationApi.getRecommendation(
        garmentType: _garmentTypeFromProductName(widget.product.name),
      );
      if (!mounted) return;
      setState(() {
        _aiRecommendedSize = result?.recommendedSize;
        _sizeRecommendationLoading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _sizeRecommendationLoading = false);
    }
  }

  final List<Map<String, dynamic>> colors = [
    {'name': 'Black', 'color': Colors.black},
    {'name': 'White', 'color': Colors.white},
    {'name': 'Gray', 'color': Colors.grey},
  ];

  static const List<String> _defaultProductImages = [
    'https://lh3.googleusercontent.com/aida-public/AB6AXuBqvJZ3YlnbQjhhX1HYEI0I3GFzEY3b7ATOMYKB7SlzXSqg8FKsKGzvq0N0NOj9WRGDvSTEhz-USPOh_XUr0ZhOSV8TRd3qiKq-xvVuG1hw6wUJ9pVvJM3kr7b8NntIIkBwIYcPxrlMR4Z1reQgWFgswj3UcyiCFehG5mEvQPetRF4qzOlZ33Ga9bQ060ZVoYGpkTRaxrR1xCB1wXqWEAFvMSWH29hAx6VjaayJqZ7ub1CWrjc4CUAlfoy0Wx7eXDofu0tZjdC4iw5g',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuCtDtg6qNUHdw7m3Pu8fzxpCgIMHIwpFHOUZHBDLANlkSYPpHGhpoqRJKLaAsAm8iJR2NAac6uuIjsvACEKF-KPbeGe0sUfnAVqKyfbte306wlnoNIXMZsllGEbDAHq8-wKC8j3e8JTnNNoP5RMY7sLNQ_DvXc02d1H9RhmOCgJxFdoUREr66S8G76_ry9SOLooUYM2GEjD7dotA9od8Tg31dux2VsqMmvwT7J0mRBWwzBPo3DQ3kO7FK5UEtF3r8fqZJqO_re2gRXd',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuDB_oc_xQcD5Uu448QUY3RZOEOd9Ua16S_OGWRymk3QokS7BI6xp26d0uZnAiK96sLS6iCC7zLZnZWR4hua1W125ihSDOVGNEBmh9KyqtjH6Cq4Z6E-YfMD2_0iwjvSZWaLi_0dFH1OMKI2kXXXu1cnsJo_uurfOyFvAmVJD7OnWv1QP-2zE1s-ANCWVIwCUY8iT30UJoZt4yWSXIoXL5dVlR3eexECFxUOZ8MDXPJj06SSUt3Xn4Xsgwr9O-zYFfq3oBU_NShRi3-L',
    'https://lh3.googleusercontent.com/aida-public/AB6AXuAfo527qrKlgw7yTKR4jBJnJaKttmLid9gnoiBaxjWES0fa9zhU6QXJrqhp4FpmrBVthSI10HnqWVsFjk_yrUMkH9gKop-xdOrf-1k8BOa89PUgjwfcshLxien-JAjr--EFDmIMoPKAImObL7O_6_1WSDnMsrjMHaeK_qbLFS_fo1wDcvLbjWgs-5M2xpg2nV2DmPthOJCO5QQBdj4rw7LQ6g7YIF-doGpL3KbCwrC_qIt-M_-KAmAR8Vk8LMsXPLOpfWRWHEkXV_SN',
  ];

  List<String> get _galleryImages {
    final productImages = widget.productImages ?? _defaultProductImages;
    if (widget.triedLookImageUrl != null && widget.triedLookImageUrl!.isNotEmpty) {
      return [widget.triedLookImageUrl!, ...productImages];
    }
    return productImages;
  }

  @override
  void initState() {
    super.initState();
    _fetchSizeRecommendation();
  }

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
      body: Stack(
        children: [
          Column(
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
                      final wasFavorite = _isFavorite;
                      setState(() {
                        if (wasFavorite) {
                          final idx = FavoritesCartStore.favorites
                              .indexWhere((e) =>
                                  e.name == widget.product.name &&
                                  e.imageUrl == widget.product.imageUrl);
                          if (idx >= 0) FavoritesCartStore.removeFavoriteAt(idx);
                        } else {
                          FavoritesCartStore.addFavorite(FavoriteItem(
                            name: widget.product.name,
                            price: widget.product.price,
                            imageUrl: widget.product.imageUrl,
                          ));
                        }
                      });
                    },
                    icon: Icon(
                      _isFavorite ? Icons.favorite : Icons.favorite_border,
                      color: _isFavorite ? Colors.red : textPrimary,
                      size: 20,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Image Gallery (smaller, tap to open full-screen)
          SizedBox(
            height: 300,
            child: PageView.builder(
              itemCount: _galleryImages.length,
              itemBuilder: (context, index) {
                final url = _galleryImages[index];
                final isTriedLook = widget.triedLookImageUrl != null && index == 0;
                return GestureDetector(
                  onTap: () => _showFullScreenImage(context, url, primaryColor),
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E1E),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          url.startsWith('http')
                              ? Image.network(
                                  url,
                                  fit: BoxFit.contain,
                                  width: double.infinity,
                                  height: double.infinity,
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
                                  errorBuilder: (_, __, ___) => const Center(
                                    child: Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48),
                                  ),
                                )
                              : Image.asset(
                                  url,
                                  fit: BoxFit.contain,
                                  width: double.infinity,
                                  height: double.infinity,
                                  errorBuilder: (_, __, ___) => const Center(
                                    child: Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48),
                                  ),
                                ),
                          if (isTriedLook)
                            Positioned(
                              left: 12,
                              bottom: 12,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.black54,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Text(
                                  'Your look',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                    fontFamily: 'SpaceGrotesk',
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ),
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
                      const SizedBox(height: 8),
                      if (_sizeRecommendationLoading)
                        const Padding(
                          padding: EdgeInsets.only(top: 4),
                          child: SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Color(0xFF06F81A),
                            ),
                          ),
                        )
                      else if (_aiRecommendedSize != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            'Size recommended by AI: $_aiRecommendedSize',
                            style: const TextStyle(
                              color: Color(0xFF06F81A),
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
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
                            child: GestureDetector(
                              onTap: _tryOnLoading ? null : _onTryOn,
                              child: AnimatedContainer(
                                duration: const Duration(milliseconds: 200),
                                height: 56,
                                decoration: BoxDecoration(
                                  color: _tryOnLoading ? accentSecondary.withValues(alpha: 0.6) : accentSecondary,
                                  borderRadius: BorderRadius.circular(28),
                                ),
                                child: Center(
                                  child: _tryOnLoading
                                      ? const SizedBox(
                                          width: 24,
                                          height: 24,
                                          child: CircularProgressIndicator(
                                            color: Color(0xFF3DDC84),
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : const Text(
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
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: GestureDetector(
                              onTap: _addedToCart
                                  ? null
                                  : () {
                                      setState(() {
                                        FavoritesCartStore.addToCart(CartItem(
                                          name: widget.product.name,
                                          size: selectedSize,
                                          price: widget.product.price,
                                          imageUrl: widget.product.imageUrl,
                                          quantity: quantity,
                                        ));
                                        _addedToCart = true;
                                      });
                                    },
                              child: AnimatedSwitcher(
                                duration: const Duration(milliseconds: 300),
                                child: Container(
                                  key: ValueKey(_addedToCart),
                                  height: 56,
                                  decoration: BoxDecoration(
                                    color: _addedToCart
                                        ? const Color(0xFF2A2A2A)
                                        : primaryColor,
                                    borderRadius: BorderRadius.circular(28),
                                  ),
                                  child: Center(
                                    child: _addedToCart
                                        ? const Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              Icon(Icons.check_circle, color: Color(0xFF06F81A), size: 24),
                                              SizedBox(width: 8),
                                              Text(
                                                'Added',
                                                style: TextStyle(
                                                  color: Color(0xFFA0A0A0),
                                                  fontSize: 18,
                                                  fontWeight: FontWeight.bold,
                                                  fontFamily: 'SpaceGrotesk',
                                                ),
                                              ),
                                            ],
                                          )
                                        : const Text(
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
          const ChatFabOverlay(),
        ],
      ),
    );
  }

  void _showFullScreenImage(BuildContext context, String url, Color primaryColor) {
    showDialog(
      context: context,
      barrierColor: Colors.black87,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: EdgeInsets.zero,
        child: Stack(
          fit: StackFit.expand,
          children: [
            InteractiveViewer(
              minScale: 0.5,
              maxScale: 4,
              child: url.startsWith('http')
                  ? Image.network(
                      url,
                      fit: BoxFit.contain,
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
                      errorBuilder: (_, __, ___) => const Center(
                        child: Icon(Icons.image_not_supported, color: Colors.white70, size: 48),
                      ),
                    )
                  : Image.asset(
                      url,
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => const Center(
                        child: Icon(Icons.image_not_supported, color: Colors.white70, size: 48),
                      ),
                    ),
            ),
            Positioned(
              top: MediaQuery.of(context).padding.top + 8,
              right: 16,
              child: IconButton(
                onPressed: () => Navigator.of(ctx).pop(),
                icon: const Icon(Icons.close, color: Colors.white, size: 28),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.black54,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _onTryOn() async {
    setState(() => _tryOnLoading = true);
    try {
      final profile = await ProfileApi.getProfile();
      final avatarUrl = profile.avatarUrl;
      if (avatarUrl == null || avatarUrl.isEmpty) {
        if (!mounted) return;
        setState(() => _tryOnLoading = false);
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            backgroundColor: const Color(0xFF1E1E1E),
            title: const Text('Full-body photo needed', style: TextStyle(color: Colors.white)),
            content: const Text(
              'Upload a full-body photo in Profile first for the best try-on result.',
              style: TextStyle(color: Color(0xFFA0A0A0)),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('OK', style: TextStyle(color: Color(0xFF06F81A))),
              ),
            ],
          ),
        );
        return;
      }
      final baseUrl = kApiBaseUrl.replaceFirst(RegExp(r'/$'), '');
      final personUrl = avatarUrl.startsWith('http') ? avatarUrl : '$baseUrl$avatarUrl';
      final personRes = await ApiClient.dio.get<List<int>>(
        personUrl,
        options: Options(responseType: ResponseType.bytes),
      );
      final personBytes = personRes.data;
      if (personBytes == null || personBytes.isEmpty) throw Exception('Could not load your photo');
      List<int> clothBytes;
      String clothFilename;
      if (widget.product.imageUrl.startsWith('http')) {
        final clothRes = await ApiClient.dio.get<List<int>>(
          widget.product.imageUrl,
          options: Options(responseType: ResponseType.bytes),
        );
        clothBytes = clothRes.data ?? [];
        clothFilename = 'cloth.png';
      } else {
        final bundle = await rootBundle.load(widget.product.imageUrl);
        clothBytes = bundle.buffer.asUint8List();
        clothFilename = widget.product.imageUrl.split('/').last;
      }
      if (clothBytes.isEmpty) throw Exception('Could not load product image');
      final resultUrl = await TryOnApi.createTryOn(
        personBytes: personBytes,
        clothBytes: clothBytes,
        personFilename: 'person.png',
        clothFilename: clothFilename,
        productName: widget.product.name,
        productImageUrl: widget.product.imageUrl,
      );
      if (!mounted) return;
      setState(() => _tryOnLoading = false);
      _showTryOnResultDialog(resultUrl);
    } catch (e) {
      if (!mounted) return;
      setState(() => _tryOnLoading = false);
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: const Color(0xFF1E1E1E),
          title: const Text('Try-on failed', style: TextStyle(color: Colors.white)),
          content: Text(
            e.toString().replaceFirst('Exception: ', ''),
            style: const TextStyle(color: Color(0xFFA0A0A0)),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('OK', style: TextStyle(color: Color(0xFF06F81A))),
            ),
          ],
        ),
      );
    }
  }

  void _showTryOnResultDialog(String resultUrl) {
    showDialog(
      context: context,
      barrierColor: Colors.black87,
      barrierDismissible: true,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(ctx).size.height * 0.85,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Stack(
                  clipBehavior: Clip.none,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Image.network(
                        resultUrl,
                        fit: BoxFit.contain,
                        width: double.infinity,
                        height: 320,
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return const SizedBox(
                            height: 320,
                            child: Center(child: CircularProgressIndicator(color: Color(0xFF06F81A))),
                          );
                        },
                        errorBuilder: (_, __, ___) => const SizedBox(
                          height: 200,
                          child: Center(child: Icon(Icons.image_not_supported, color: Colors.white70, size: 48)),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Material(
                        color: Colors.black54,
                        shape: const CircleBorder(),
                        child: InkWell(
                          onTap: () => Navigator.pop(ctx),
                          customBorder: const CircleBorder(),
                          child: const Padding(
                            padding: EdgeInsets.all(8),
                            child: Icon(Icons.close, color: Colors.white, size: 24),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  'Your try-on result',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'SpaceGrotesk',
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => Navigator.pop(ctx),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF06F81A),
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
                    ),
                    child: const Text('Close'),
                  ),
                ),
              ],
            ),
          ),
        ),
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
