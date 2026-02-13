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
      // Increased timeouts for slow backend / long VTO jobs on Render.
      // 5 minutes is usually enough for HF Space cold start + try-on.
      connectTimeout: const Duration(seconds: 90),
      receiveTimeout: const Duration(minutes: 5),
      sendTimeout: const Duration(minutes: 5),
      headers: {'Content-Type': 'application/json'},
    ),
  );
}
