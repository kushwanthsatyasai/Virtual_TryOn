import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

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

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<String> uploadFullBodyPhoto({
    required File photoFile,
    String? token,
  }) async {
    final accessToken = token ?? await getToken();
    if (accessToken == null || accessToken.isEmpty) {
      throw Exception('Missing access token');
    }

    final filename = photoFile.path.split(Platform.pathSeparator).last;
    final form = FormData.fromMap({
      'photo': await MultipartFile.fromFile(photoFile.path, filename: filename),
    });

    final Response res = await ApiClient.dio.post(
      '/api/v1/profile/full-body-photo',
      data: form,
      options: Options(
        headers: {'Authorization': 'Bearer $accessToken'},
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

