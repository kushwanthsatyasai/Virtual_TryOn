import 'package:flutter/material.dart';
import 'dart:ui';
import '../search/search_screen.dart';
import '../product/product_detail_screen.dart';
import '../../widgets/bottom_navigation_bar.dart';
import '../../widgets/chat_fab_overlay.dart';
import '../../models/tried_look.dart';
import '../../services/try_on_api.dart';
import '../../services/auth_api.dart';
import '../../services/recommendations_api.dart';
import '../../data/products_data.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<TriedLook> _triedLooks = [];
  bool _loadingTriedLooks = true;
  bool _triedLooksError = false;

  List<RecommendationItem> _recommendations = [];
  bool _loadingRecommendations = true;

  @override
  void initState() {
    super.initState();
    _loadTriedLooks();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    setState(() => _loadingRecommendations = true);
    try {
      final list = await RecommendationsApi.getRecommendations(limit: 10);
      if (mounted) setState(() {
        _recommendations = list;
        _loadingRecommendations = false;
      });
    } catch (_) {
      if (mounted) setState(() {
        _recommendations = [];
        _loadingRecommendations = false;
      });
    }
  }

  Future<void> _loadTriedLooks() async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      if (mounted) setState(() { _loadingTriedLooks = false; _triedLooks = []; });
      return;
    }
    setState(() { _loadingTriedLooks = true; _triedLooksError = false; });
    try {
      final list = await TryOnApi.getTryOnHistory(limit: 20);
      if (mounted) setState(() { _triedLooks = list; _loadingTriedLooks = false; });
    } catch (_) {
      if (mounted) setState(() { _triedLooksError = true; _loadingTriedLooks = false; _triedLooks = []; });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Colors from design
    const backgroundColor = Color(0xFF121212);
    const textPrimary = Color(0xFFFFFFFF);

    return Scaffold(
      backgroundColor: backgroundColor,
      // App Bar
      appBar: AppBar(
        backgroundColor: backgroundColor.withValues(alpha: 0.8),
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
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SearchScreen()),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      
      // Body
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Recent Looks Section (from virtual try-on)
            _buildRecentLooksSection(),
            
            // Recommended for you (fashion recommendation API)
            _buildRecommendedSection(),
            
            // Trending Section (products; tap opens product detail)
            _buildTrendingSection(),
            
            // Popular Brands Section
            _buildBrandsSection(),
            ],
            ),
          ),
          const ChatFabOverlay(),
        ],
      ),

      // Bottom Navigation Bar
             bottomNavigationBar: const CustomBottomNavigationBar(
         currentIndex: 0,
       ),
    );
  }

  Widget _buildRecentLooksSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(16, 24, 16, 16),
          child: Text(
            'Recent Looks',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFFFFFFF),
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ),
        SizedBox(
          height: _triedLooks.isEmpty && !_loadingTriedLooks ? 72 : 280,
          child: _loadingTriedLooks
              ? const Center(child: CircularProgressIndicator(color: Color(0xFF06F81A)))
              : _triedLooks.isEmpty
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24),
                        child: Text(
                          _triedLooksError ? 'Could not load looks' : 'No looks tried',
                          style: const TextStyle(
                            color: Color(0xFFA0A0A0),
                            fontSize: 16,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                      ),
                    )
                  : ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _triedLooks.length,
                      itemBuilder: (context, index) {
                        final look = _triedLooks[index];
                        return Padding(
                          padding: const EdgeInsets.only(right: 16),
                          child: _buildTriedLookCard(look),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  Widget _buildTriedLookCard(TriedLook look) {
    final productName = look.metadata?.productName ?? 'Your look';
    final productImageUrl = look.clothImageUrl ?? look.metadata?.productImageUrl ?? '';
    final product = ProductItem(
      name: productName,
      price: 0,
      imageUrl: productImageUrl.isNotEmpty ? productImageUrl : 'https://via.placeholder.com/400',
    );
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailScreen(
              product: product,
              triedLookImageUrl: look.resultImageUrl,
              productImages: productImageUrl.isNotEmpty ? [productImageUrl] : null,
            ),
          ),
        );
      },
      child: SizedBox(
        width: 176,
        height: 280,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  look.resultImageUrl,
                  fit: BoxFit.cover,
                  width: double.infinity,
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
                    child: const Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              productName,
              style: const TextStyle(
                color: Color(0xFFA0A0A0),
                fontSize: 14,
                fontWeight: FontWeight.w500,
                fontFamily: 'SpaceGrotesk',
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendedSection() {
    if (_loadingRecommendations && _recommendations.isEmpty) {
      return const Padding(
        padding: EdgeInsets.fromLTRB(16, 24, 16, 16),
        child: SizedBox(
          height: 40,
          child: Center(
            child: CircularProgressIndicator(color: Color(0xFF06F81A), strokeWidth: 2),
          ),
        ),
      );
    }
    if (_recommendations.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(16, 24, 16, 16),
          child: Text(
            'Recommended for you',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFFFFFFF),
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ),
        SizedBox(
          height: 280,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: _recommendations.length,
            itemBuilder: (context, index) {
              final rec = _recommendations[index];
              final match = allProducts.where((p) => p.name == rec.name).toList();
              final product = match.isEmpty ? ProductItem(name: rec.name, price: rec.price, imageUrl: rec.imageUrl) : match.first;
              return Padding(
                padding: const EdgeInsets.only(right: 16),
                child: _buildRecommendationCard(product, rec.reason),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationCard(ProductItem product, String reason) {
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
      child: SizedBox(
        width: 176,
        height: 280,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: product.imageUrl.startsWith('http')
                    ? Image.network(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        width: double.infinity,
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Center(child: CircularProgressIndicator(color: const Color(0xFF06F81A), value: loadingProgress.expectedTotalBytes != null ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes! : null));
                        },
                        errorBuilder: (_, __, ___) => Container(color: const Color(0xFF1E1E1E), child: const Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48)),
                      )
                    : Image.asset(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        width: double.infinity,
                        errorBuilder: (_, __, ___) => Container(color: const Color(0xFF1E1E1E), child: const Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48)),
                      ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              product.name,
              style: const TextStyle(color: Color(0xFFA0A0A0), fontSize: 14, fontWeight: FontWeight.w500, fontFamily: 'SpaceGrotesk'),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (reason.isNotEmpty)
              Text(
                reason,
                style: const TextStyle(color: Color(0xFF06F81A), fontSize: 11, fontFamily: 'SpaceGrotesk'),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrendingSection() {
    final trending = allProducts.length > 6 ? allProducts.sublist(0, 6) : allProducts;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(16, 24, 16, 16),
          child: Text(
            'Trending',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFFFFFFF),
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ),
        SizedBox(
          height: 280,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: trending.length,
            itemBuilder: (context, index) {
              final product = trending[index];
              return Padding(
                padding: const EdgeInsets.only(right: 16),
                child: _buildTrendingCard(product),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTrendingCard(ProductItem product) {
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
      child: SizedBox(
        width: 176,
        height: 280,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: product.imageUrl.startsWith('http')
                    ? Image.network(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        width: double.infinity,
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
                          child: const Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48),
                        ),
                      )
                    : Image.asset(
                        product.imageUrl,
                        fit: BoxFit.cover,
                        width: double.infinity,
                        errorBuilder: (_, __, ___) => Container(
                          color: const Color(0xFF1E1E1E),
                          child: const Icon(Icons.image_not_supported, color: Color(0xFFA0A0A0), size: 48),
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              product.name,
              style: const TextStyle(
                color: Color(0xFFA0A0A0),
                fontSize: 14,
                fontWeight: FontWeight.w500,
                fontFamily: 'SpaceGrotesk',
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              '₹${product.price.toStringAsFixed(2)}',
              style: const TextStyle(
                color: Color(0xFF06F81A),
                fontSize: 14,
                fontWeight: FontWeight.w600,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
          ],
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

  Widget _buildBrandsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
          child: Text(
            'Popular Brands',
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFFFFFFF),
              fontFamily: 'SpaceGrotesk',
            ),
          ),
        ),
        SizedBox(
          height: 120,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: [
              _buildBrandIcon('Nike', 'assets/icons/nike_logo.png'),
              _buildBrandIcon('Adidas', 'assets/icons/adidas_logo.png'),
              _buildBrandIcon('Puma', 'assets/icons/puma_logo.png'),
              _buildBrandIcon('Levi\'s', 'assets/icons/levis_logo.png'),
              _buildBrandIcon('Zara', 'assets/icons/zara_logo.png'),
              _buildBrandIcon('H&M', 'assets/icons/hm_logo.png'),
              _buildBrandIcon('Uniqlo', 'assets/icons/uniqlo_logo.png'),
              _buildBrandIcon('Gap', 'assets/icons/gap_logo.png'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBrandIcon(String brandName, String iconPath) {
    return Padding(
      padding: const EdgeInsets.only(right: 20),
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF1E1E1E),
              border: Border.all(
                color: const Color(0xFF06F81A).withValues(alpha: 0.3),
                width: 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF06F81A).withValues(alpha: 0.1),
                  blurRadius: 8,
                  spreadRadius: 0,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipOval(
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF2A2A2A),
                ),
                child: Center(
                  child: _buildBrandLogo(brandName),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            brandName,
            style: const TextStyle(
              color: Color(0xFFA0A0A0),
              fontSize: 12,
              fontWeight: FontWeight.w500,
              fontFamily: 'SpaceGrotesk',
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildBrandLogo(String brandName) {
    switch (brandName.toLowerCase()) {
      case 'nike':
        return _buildNikeLogo();
      case 'adidas':
        return _buildAdidasLogo();
      case 'puma':
        return _buildPumaLogo();
      case 'levi\'s':
        return _buildLevisLogo();
      case 'zara':
        return _buildZaraLogo();
      case 'h&m':
        return _buildHMLogo();
      case 'uniqlo':
        return _buildUniqloLogo();
      case 'gap':
        return _buildGapLogo();
      default:
        return Icon(
          Icons.shopping_bag,
          size: 40,
          color: const Color(0xFF06F81A),
        );
    }
  }

  Widget _buildNikeLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: NikeLogoPainter(),
    );
  }

  Widget _buildAdidasLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: AdidasLogoPainter(),
    );
  }

  Widget _buildPumaLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: PumaLogoPainter(),
    );
  }

  Widget _buildLevisLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: LevisLogoPainter(),
    );
  }

  Widget _buildZaraLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: ZaraLogoPainter(),
    );
  }

  Widget _buildHMLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: HMLogoPainter(),
    );
  }

  Widget _buildUniqloLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: UniqloLogoPainter(),
    );
  }

  Widget _buildGapLogo() {
    return CustomPaint(
      size: const Size(50, 50),
      painter: GapLogoPainter(),
    );
  }
}

// Custom Painters for Brand Logos
class NikeLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    final path = Path();
    path.moveTo(size.width * 0.1, size.height * 0.2);
    path.quadraticBezierTo(
      size.width * 0.3, size.height * 0.1,
      size.width * 0.5, size.height * 0.3,
    );
    path.quadraticBezierTo(
      size.width * 0.7, size.height * 0.5,
      size.width * 0.9, size.height * 0.8,
    );
    path.lineTo(size.width * 0.8, size.height * 0.9);
    path.quadraticBezierTo(
      size.width * 0.6, size.height * 0.6,
      size.width * 0.4, size.height * 0.4,
    );
    path.quadraticBezierTo(
      size.width * 0.2, size.height * 0.3,
      size.width * 0.1, size.height * 0.2,
    );
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class AdidasLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw three leaves
    final leafPath1 = Path();
    leafPath1.moveTo(size.width * 0.2, size.height * 0.8);
    leafPath1.quadraticBezierTo(
      size.width * 0.3, size.height * 0.6,
      size.width * 0.4, size.height * 0.4,
    );
    leafPath1.quadraticBezierTo(
      size.width * 0.5, size.height * 0.2,
      size.width * 0.6, size.height * 0.1,
    );
    leafPath1.lineTo(size.width * 0.7, size.height * 0.2);
    leafPath1.quadraticBezierTo(
      size.width * 0.6, size.height * 0.4,
      size.width * 0.5, size.height * 0.6,
    );
    leafPath1.quadraticBezierTo(
      size.width * 0.4, size.height * 0.8,
      size.width * 0.2, size.height * 0.8,
    );
    leafPath1.close();

    final leafPath2 = Path();
    leafPath2.moveTo(size.width * 0.4, size.height * 0.8);
    leafPath2.quadraticBezierTo(
      size.width * 0.5, size.height * 0.6,
      size.width * 0.6, size.height * 0.4,
    );
    leafPath2.quadraticBezierTo(
      size.width * 0.7, size.height * 0.2,
      size.width * 0.8, size.height * 0.1,
    );
    leafPath2.lineTo(size.width * 0.9, size.height * 0.2);
    leafPath2.quadraticBezierTo(
      size.width * 0.8, size.height * 0.4,
      size.width * 0.7, size.height * 0.6,
    );
    leafPath2.quadraticBezierTo(
      size.width * 0.6, size.height * 0.8,
      size.width * 0.4, size.height * 0.8,
    );
    leafPath2.close();

    final leafPath3 = Path();
    leafPath3.moveTo(size.width * 0.6, size.height * 0.8);
    leafPath3.quadraticBezierTo(
      size.width * 0.7, size.height * 0.6,
      size.width * 0.8, size.height * 0.4,
    );
    leafPath3.quadraticBezierTo(
      size.width * 0.9, size.height * 0.2,
      size.width * 1.0, size.height * 0.1,
    );
    leafPath3.lineTo(size.width * 0.9, size.height * 0.2);
    leafPath3.quadraticBezierTo(
      size.width * 0.8, size.height * 0.4,
      size.width * 0.7, size.height * 0.6,
    );
    leafPath3.quadraticBezierTo(
      size.width * 0.6, size.height * 0.8,
      size.width * 0.6, size.height * 0.8,
    );
    leafPath3.close();

    canvas.drawPath(leafPath1, paint);
    canvas.drawPath(leafPath2, paint);
    canvas.drawPath(leafPath3, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class PumaLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw Puma jumping logo
    final path = Path();
    path.moveTo(size.width * 0.2, size.height * 0.8);
    path.quadraticBezierTo(
      size.width * 0.3, size.height * 0.6,
      size.width * 0.4, size.height * 0.4,
    );
    path.quadraticBezierTo(
      size.width * 0.5, size.height * 0.2,
      size.width * 0.6, size.height * 0.1,
    );
    path.quadraticBezierTo(
      size.width * 0.7, size.height * 0.2,
      size.width * 0.8, size.height * 0.4,
    );
    path.quadraticBezierTo(
      size.width * 0.7, size.height * 0.6,
      size.width * 0.6, size.height * 0.8,
    );
    path.quadraticBezierTo(
      size.width * 0.5, size.height * 0.7,
      size.width * 0.4, size.height * 0.6,
    );
    path.quadraticBezierTo(
      size.width * 0.3, size.height * 0.7,
      size.width * 0.2, size.height * 0.8,
    );
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class LevisLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw Levi's batwing logo
    final path = Path();
    path.moveTo(size.width * 0.1, size.height * 0.5);
    path.lineTo(size.width * 0.3, size.height * 0.3);
    path.lineTo(size.width * 0.5, size.height * 0.5);
    path.lineTo(size.width * 0.7, size.height * 0.3);
    path.lineTo(size.width * 0.9, size.height * 0.5);
    path.lineTo(size.width * 0.7, size.height * 0.7);
    path.lineTo(size.width * 0.5, size.height * 0.5);
    path.lineTo(size.width * 0.3, size.height * 0.7);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class ZaraLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw ZARA text-like logo
    final textStyle = TextStyle(
      color: const Color(0xFF000000),
      fontSize: 24,
      fontWeight: FontWeight.bold,
      fontFamily: 'SpaceGrotesk',
    );
    
    final textSpan = TextSpan(text: 'ZARA', style: textStyle);
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(
      (size.width - textPainter.width) / 2,
      (size.height - textPainter.height) / 2,
    ));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class HMLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw H&M logo
    final textStyle = TextStyle(
      color: const Color(0xFF000000),
      fontSize: 20,
      fontWeight: FontWeight.bold,
      fontFamily: 'SpaceGrotesk',
    );
    
    final textSpan = TextSpan(text: 'H&M', style: textStyle);
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(
      (size.width - textPainter.width) / 2,
      (size.height - textPainter.height) / 2,
    ));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class UniqloLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw Uniqlo logo
    final textStyle = TextStyle(
      color: const Color(0xFF000000),
      fontSize: 18,
      fontWeight: FontWeight.bold,
      fontFamily: 'SpaceGrotesk',
    );
    
    final textSpan = TextSpan(text: 'UNIQLO', style: textStyle);
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(
      (size.width - textPainter.width) / 2,
      (size.height - textPainter.height) / 2,
    ));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class GapLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF000000)
      ..style = PaintingStyle.fill;

    // Draw Gap logo
    final textStyle = TextStyle(
      color: const Color(0xFF000000),
      fontSize: 22,
      fontWeight: FontWeight.bold,
      fontFamily: 'SpaceGrotesk',
    );
    
    final textSpan = TextSpan(text: 'GAP', style: textStyle);
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(
      (size.width - textPainter.width) / 2,
      (size.height - textPainter.height) / 2,
    ));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}