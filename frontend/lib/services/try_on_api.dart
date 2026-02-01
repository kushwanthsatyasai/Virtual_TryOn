import 'package:dio/dio.dart';

import 'api_client.dart';
import 'auth_api.dart';
import '../models/tried_look.dart';

class TryOnApi {
  TryOnApi._();

  static Future<List<TriedLook>> getTryOnHistory({int skip = 0, int limit = 20}) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      throw Exception('Not logged in');
    }
    final Response res = await ApiClient.dio.get(
      '/api/v1/try-on/history',
      queryParameters: {'skip': skip, 'limit': limit},
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
    final data = res.data as Map<String, dynamic>;
    final items = data['items'] as List<dynamic>? ?? [];
    final baseUrl = kApiBaseUrl.replaceFirst(RegExp(r'/$'), '');
    return items
        .map((e) => TriedLook.fromJson(e as Map<String, dynamic>, baseUrl))
        .toList();
  }

  /// Run virtual try-on: person image + cloth image -> result image URL.
  static Future<String> createTryOn({
    required List<int> personBytes,
    required List<int> clothBytes,
    required String personFilename,
    required String clothFilename,
    String? productName,
    String? productImageUrl,
  }) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      throw Exception('Not logged in');
    }
    final formData = FormData.fromMap({
      'person': MultipartFile.fromBytes(
        personBytes,
        filename: personFilename.endsWith('.png') ? personFilename : '$personFilename.png',
      ),
      'cloth': MultipartFile.fromBytes(
        clothBytes,
        filename: clothFilename.endsWith('.png') ? clothFilename : '$clothFilename.png',
      ),
      if (productName != null && productName.isNotEmpty) 'product_name': productName,
      if (productImageUrl != null && productImageUrl.isNotEmpty) 'product_image_url': productImageUrl,
    });
    final Response res = await ApiClient.dio.post(
      '/api/v1/try-on',
      data: formData,
      options: Options(
        headers: {'Authorization': 'Bearer $token'},
        sendTimeout: const Duration(seconds: 180),
        receiveTimeout: const Duration(seconds: 180),
      ),
    );
    final data = res.data as Map<String, dynamic>;
    final resultPath = data['result'] as String?;
    final resultUrlFromApi = data['result_url'] as String?;
    if ((resultPath == null || resultPath.isEmpty) && (resultUrlFromApi == null || resultUrlFromApi.isEmpty)) {
      throw Exception('Try-on succeeded but no result URL');
    }
    final baseUrl = kApiBaseUrl.replaceFirst(RegExp(r'/$'), '');
    final path = resultUrlFromApi ?? resultPath!;
    if (path.startsWith('http')) return path;
    return path.startsWith('/') ? '$baseUrl$path' : '$baseUrl/$path';
  }
}
