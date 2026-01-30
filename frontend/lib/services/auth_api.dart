import 'package:dio/dio.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';

class AuthApi {
  AuthApi._();

  static const _tokenKey = 'access_token';

  static Future<String> register(Map<String, dynamic> payload) async {
    final Response res = await ApiClient.dio.post('/auth/register', data: payload);
    final data = res.data as Map<String, dynamic>;
    final token = data['access_token'] as String?;
    if (token == null || token.isEmpty) {
      throw Exception('Registration succeeded but token missing');
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    return token;
  }

  /// Login with email or username + password. Backend accepts both in "username" field.
  static Future<String> login(String usernameOrEmail, String password) async {
    final Response res = await ApiClient.dio.post(
      '/auth/login',
      data: {'username': usernameOrEmail.trim(), 'password': password},
      options: Options(
        contentType: Headers.formUrlEncodedContentType,
        sendTimeout: const Duration(seconds: 120),
        receiveTimeout: const Duration(seconds: 120),
      ),
    );
    final data = res.data as Map<String, dynamic>;
    final token = data['access_token'] as String?;
    if (token == null || token.isEmpty) {
      throw Exception('Login succeeded but token missing');
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    return token;
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<String> uploadFullBodyPhoto({
    required XFile photoFile,
    String? token,
  }) async {
    final accessToken = token ?? await getToken();
    if (accessToken == null || accessToken.isEmpty) {
      throw Exception('Missing access token');
    }

    final filename = photoFile.name;
    final bytes = await photoFile.readAsBytes();
    return uploadFullBodyPhotoBytes(
      bytes: bytes,
      filename: filename,
      token: accessToken,
    );
  }

  static Future<String> uploadFullBodyPhotoBytes({
    required List<int> bytes,
    required String filename,
    String? token,
  }) async {
    final accessToken = token ?? await getToken();
    if (accessToken == null || accessToken.isEmpty) {
      throw Exception('Missing access token');
    }

    final form = FormData.fromMap({
      'photo': MultipartFile.fromBytes(bytes, filename: filename),
    });

    final Response res = await ApiClient.dio.post(
      '/api/v1/profile/full-body-photo',
      data: form,
      options: Options(
        headers: {'Authorization': 'Bearer $accessToken'},
        sendTimeout: const Duration(seconds: 120),
        receiveTimeout: const Duration(seconds: 120),
      ),
    );

    final data = res.data as Map<String, dynamic>;
    final url = data['avatar_url'] as String?;
    if (url == null || url.isEmpty) {
      throw Exception('Upload succeeded but avatar_url missing');
    }
    return url;
  }
}

