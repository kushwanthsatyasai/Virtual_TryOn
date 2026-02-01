import 'package:dio/dio.dart';

import 'api_client.dart' show ApiClient, kApiBaseUrl;
import 'auth_api.dart';

/// Fashion recommendations from backend GET /api/v1/recommendations.
class RecommendationsApi {
  RecommendationsApi._();

  static const String _path = '/api/v1/recommendations';

  /// Fetches personalized recommendations. Returns list of { name, price, imageUrl, reason }.
  static Future<List<RecommendationItem>> getRecommendations({
    int limit = 10,
    String? category,
    bool excludeTried = false,
  }) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) return [];
    try {
      final res = await ApiClient.dio.get(
        _path,
        queryParameters: {
          'limit': limit,
          if (category != null && category.isNotEmpty) 'category': category,
          'exclude_tried': excludeTried,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
          validateStatus: (s) => s != null && s < 500,
        ),
      );
      if (res.statusCode != 200) return [];
      final data = res.data as Map<String, dynamic>?;
      final list = data?['recommendations'] as List<dynamic>?;
      if (list == null) return [];
      final baseUrl = kApiBaseUrl.replaceFirst(RegExp(r'/$'), '');
      return list.map((e) {
        final map = e as Map<String, dynamic>? ?? {};
        final name = map['name'] as String? ?? '';
        final price = (map['price'] as num?)?.toDouble() ?? 0;
        final image = map['image_url'] as String? ?? map['image'] as String? ?? '';
        final imageUrl = image.startsWith('http') ? image : (image.startsWith('/') ? '$baseUrl$image' : image);
        final reason = map['reason'] as String? ?? '';
        return RecommendationItem(name: name, price: price, imageUrl: imageUrl, reason: reason);
      }).where((e) => e.name.isNotEmpty).toList();
    } catch (_) {
      return [];
    }
  }
}

class RecommendationItem {
  final String name;
  final double price;
  final String imageUrl;
  final String reason;

  RecommendationItem({
    required this.name,
    required this.price,
    required this.imageUrl,
    this.reason = '',
  });
}
