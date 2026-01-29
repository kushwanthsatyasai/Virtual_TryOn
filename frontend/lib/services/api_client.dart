import 'package:dio/dio.dart';

// Default: deployed Render backend.
// For local dev, override at build time with:
// flutter run --dart-define=API_BASE_URL=http://localhost:8000
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://virtue-try-on.onrender.com',
);

class ApiClient {
  ApiClient._();

  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: kApiBaseUrl,
      // Render can be slow on cold start; give generous timeouts.
      connectTimeout: const Duration(seconds: 60),
      receiveTimeout: const Duration(seconds: 90),
      sendTimeout: const Duration(seconds: 90),
      headers: {'Content-Type': 'application/json'},
    ),
  );
}

