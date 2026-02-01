import 'package:dio/dio.dart';

import 'api_client.dart';
import 'auth_api.dart';

/// Size recommendation by AI using the user's profile (full-body) photo.
class SizeRecommendationApi {
  SizeRecommendationApi._();

  /// GET /api/v1/size/recommend?garment_type=shirt
  /// Returns { recommended_size, confidence, fit_notes }. Requires profile avatar.
  static Future<SizeRecommendationResult?> getRecommendation({
    String garmentType = 'shirt',
  }) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) return null;
    try {
      final res = await ApiClient.dio.get(
        '/api/v1/size/recommend',
        queryParameters: {'garment_type': garmentType},
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
          validateStatus: (s) => s != null && s < 500,
        ),
      );
      if (res.statusCode != 200) return null;
      final data = res.data as Map<String, dynamic>?;
      if (data == null) return null;
      final size = data['recommended_size'] as String?;
      if (size == null || size.isEmpty) return null;
      return SizeRecommendationResult(
        recommendedSize: size,
        confidence: (data['confidence'] as num?)?.toDouble(),
        fitNotes: data['fit_notes'] as String? ?? '',
      );
    } catch (_) {
      return null;
    }
  }
}

class SizeRecommendationResult {
  final String recommendedSize;
  final double? confidence;
  final String fitNotes;

  SizeRecommendationResult({
    required this.recommendedSize,
    this.confidence,
    this.fitNotes = '',
  });
}
