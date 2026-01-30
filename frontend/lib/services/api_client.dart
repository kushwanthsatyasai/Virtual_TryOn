import 'package:dio/dio.dart';

// Default: Render backend (online).
// For local dev, override at build time with:
// flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://virtue-try-on.onrender.com',
);

class ApiClient {
  ApiClient._();

  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: kApiBaseUrl,
      // Increased timeouts for slow backend (e.g. Render cold start, uploads).
      connectTimeout: const Duration(seconds: 60),
      receiveTimeout: const Duration(seconds: 120),
      sendTimeout: const Duration(seconds: 120),
      headers: {'Content-Type': 'application/json'},
    ),
  );
}
