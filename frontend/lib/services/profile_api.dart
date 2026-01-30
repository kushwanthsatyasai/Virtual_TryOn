import 'package:dio/dio.dart';

import 'api_client.dart';
import 'auth_api.dart';
import '../models/user_profile.dart';

class ProfileApi {
  ProfileApi._();

  static Future<UserProfile> getProfile() async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      throw Exception('Not logged in');
    }
    final Response res = await ApiClient.dio.get(
      '/api/v1/profile/me',
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
    final data = res.data as Map<String, dynamic>;
    return UserProfile.fromJson(data);
  }

  static Future<UserProfile> updateProfile(Map<String, dynamic> payload) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      throw Exception('Not logged in');
    }
    final Response res = await ApiClient.dio.patch(
      '/api/v1/users/me',  // PATCH only on users/me
      data: payload,
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
    final data = res.data as Map<String, dynamic>;
    return UserProfile.fromJson(data);
  }
}
