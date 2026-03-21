import 'dart:math';

import 'package:dio/dio.dart';

import '../models/product_item.dart';
import 'recommendations_api.dart';

/// One tile for the product detail "You may also like" strip.
class DetailRecommendedProduct {
  final ProductItem item;
  /// Short badge, e.g. "Online" for third-party catalog.
  final String badge;

  const DetailRecommendedProduct({
    required this.item,
    this.badge = '',
  });
}

/// Recommendations for the product detail strip.
///
/// Primary source is your backend recommendations engine (which can use visual similarity).
/// If the backend returns too few items, we backfill with FakeStore similar items.
class ProductDetailRecommendationsService {
  ProductDetailRecommendationsService._();

  static final Dio _externalDio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 12),
      receiveTimeout: const Duration(seconds: 12),
      validateStatus: (s) => s != null && s < 500,
    ),
  );

  static const int _targetMin = 6;
  static const int _targetMax = 12;
  static const double _usdToInr = 85;

  static String _norm(String s) =>
      s.trim().toLowerCase().replaceAll(RegExp(r'\s+'), ' ');

  /// Returns true if [p] is a duplicate of something already in [seenNames] (by normalized name).
  static bool _isDuplicate(Set<String> seenNames, ProductItem p) {
    final n = _norm(p.name);
    if (n.isEmpty || seenNames.contains(n)) return true;
    seenNames.add(n);
    return false;
  }

  static String _fakeStoreCategoryForProduct(ProductItem current) {
    final n = current.name.toLowerCase();
    if (n.contains('dress') ||
        n.contains('skirt') ||
        n.contains('women') ||
        n.contains('blouse')) {
      return "women's clothing";
    }
    return "men's clothing";
  }

  static Future<void> _appendFakeStore(
    List<DetailRecommendedProduct> out,
    Set<String> seenNames,
    ProductItem current,
  ) async {
    final category = _fakeStoreCategoryForProduct(current);
    final otherCategory =
        category == "men's clothing" ? "women's clothing" : "men's clothing";
    final categoriesToTry = <String>[category, otherCategory];

    for (final cat in categoriesToTry) {
      if (out.length >= _targetMax) break;
      final url =
          'https://fakestoreapi.com/products/category/${Uri.encodeComponent(cat)}';

      try {
        final res = await _externalDio.get<List<dynamic>>(url);
        if (res.statusCode != 200 || res.data == null) continue;

        final rnd = Random();
        final list = List<Map<String, dynamic>>.from(
          res.data!.whereType<Map<String, dynamic>>(),
        )..shuffle(rnd);

        for (final raw in list) {
          if (out.length >= _targetMax) break;
          final title = (raw['title'] as String?)?.trim() ?? '';
          if (title.isEmpty) continue;
          final img = (raw['image'] as String?)?.trim() ?? '';
          if (img.isEmpty || !img.startsWith('http')) continue;
          final usd = (raw['price'] as num?)?.toDouble() ?? 0;
          final inr = (usd * _usdToInr).clamp(1.0, 999999.0);

          final item = ProductItem(
            name: title,
            price: inr,
            imageUrl: img,
            isExternalCatalog: true,
          );
          if (_isDuplicate(seenNames, item)) continue;

          out.add(DetailRecommendedProduct(item: item, badge: 'Online'));
        }
      } catch (_) {
        // Offline / API errors: keep partial list
      }
    }
  }

  /// Loads up to [_targetMax] items from the backend recommendations engine, then
  /// backfills with FakeStore if the backend returns too few items.
  static Future<List<DetailRecommendedProduct>> loadForProduct(
    ProductItem current,
  ) async {
    final seenNames = <String>{_norm(current.name)};
    final out = <DetailRecommendedProduct>[];

    try {
      final backend = await RecommendationsApi.getRecommendations(
        limit: _targetMax,
        excludeTried: true,
      );
      for (final r in backend) {
        if (r.name.isEmpty || r.imageUrl.isEmpty) continue;
        final item = ProductItem(
          name: r.name,
          price: r.price,
          imageUrl: r.imageUrl,
        );
        if (_isDuplicate(seenNames, item)) continue;
        final badge = r.reason.trim().isNotEmpty ? 'For you' : '';
        out.add(DetailRecommendedProduct(item: item, badge: badge));
        if (out.length >= _targetMax) break;
      }
    } catch (_) {
      // Optional when not logged in
    }

    if (out.length < _targetMin) {
      await _appendFakeStore(out, seenNames, current);
    }

    return out.take(_targetMax).toList();
  }
}
