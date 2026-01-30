import 'package:dio/dio.dart';

import 'api_client.dart';
import 'auth_api.dart';

class ChatApi {
  ChatApi._();

  /// Send a message to the AI fashion assistant.
  /// Returns the AI response and conversation_id for follow-up messages.
  static Future<ChatSendResponse> sendMessage({
    required String message,
    int? conversationId,
  }) async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      throw Exception('Not logged in');
    }
    final Response res = await ApiClient.dio.post(
      '/api/v1/chat/send',
      data: <String, dynamic>{
        'message': message,
        if (conversationId != null) 'conversation_id': conversationId,
      },
      options: Options(
        headers: {'Authorization': 'Bearer $token'},
        sendTimeout: const Duration(seconds: 120),
        receiveTimeout: const Duration(seconds: 120),
      ),
    );
    final data = res.data as Map<String, dynamic>;
    return ChatSendResponse(
      message: data['message'] as String? ?? '',
      conversationId: (data['conversation_id'] as num?)?.toInt() ?? 0,
      model: data['model'] as String?,
    );
  }
}

class ChatSendResponse {
  final String message;
  final int conversationId;
  final String? model;

  ChatSendResponse({
    required this.message,
    required this.conversationId,
    this.model,
  });
}
