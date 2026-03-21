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

  /// Google sign-in entrypoint.
  ///
  /// Backend behavior:
  /// - existing user: returns `access_token` so the app can immediately sign in
  /// - new user: returns `needs_signup=true` and no token; app should route to signup screens
  static Future<GoogleLoginResult> googleLogin({
    required String email,
    required String fullName,
    required String googleId,
    String? idToken,
  }) async {
    final res = await ApiClient.dio.post(
      '/auth/google-login',
      data: {
        'email': email,
        'full_name': fullName,
        'google_id': googleId,
        'id_token': idToken,
      },
      options: Options(
        contentType: Headers.jsonContentType,
        sendTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
      ),
    );

    final data = res.data as Map<String, dynamic>;
    final needsSignup = data['needs_signup'] as bool? ?? false;
    final token = data['access_token'] as String?;

    if (token != null && token.isNotEmpty) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, token);
    }

    return GoogleLoginResult(
      needsSignup: needsSignup,
      accessToken: token,
      email: data['email'] as String? ?? email,
      fullName: data['full_name'] as String? ?? fullName,
    );
  }

  /// Request an OTP for password reset.
  /// In DEBUG backend mode without SMTP, response may include `dev_otp`.
  static Future<String?> requestPasswordResetOtp({
    required String email,
  }) async {
    final res = await ApiClient.dio.post(
      '/auth/password-reset/request-otp',
      data: {
        'email': email,
      },
      options: Options(
        contentType: Headers.jsonContentType,
        sendTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
      ),
    );
    final data = res.data as Map<String, dynamic>? ?? {};
    final devOtp = data['dev_otp'] as String?;
    return devOtp;
  }

  /// Confirm OTP and reset password.
  static Future<void> confirmPasswordReset({
    required String email,
    required String otp,
    required String newPassword,
  }) async {
    await ApiClient.dio.post(
      '/auth/password-reset/confirm',
      data: {
        'email': email,
        'otp': otp,
        'new_password': newPassword,
      },
      options: Options(
        contentType: Headers.jsonContentType,
        sendTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
      ),
    );
  }
}

class GoogleLoginResult {
  final bool needsSignup;
  final String? accessToken;
  final String email;
  final String fullName;

  GoogleLoginResult({
    required this.needsSignup,
    required this.accessToken,
    required this.email,
    required this.fullName,
  });
}

