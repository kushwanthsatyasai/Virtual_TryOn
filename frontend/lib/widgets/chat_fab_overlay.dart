import 'package:flutter/material.dart';

import '../services/auth_api.dart';
import '../services/chat_api.dart';
import '../services/profile_api.dart';

/// App theme colors (same as app theme)
const _backgroundColor = Color(0xFF121212);
const _cardBackground = Color(0xFF1E1E1E);
const _primaryColor = Color(0xFF06F81A);
const _textPrimary = Color(0xFFFFFFFF);
const _textSecondary = Color(0xFFA0A0A0);

/// Floating chat button at bottom-right. Tap to open a small chat window.
/// Use as overlay: Stack(children: [body, ChatFabOverlay()]).
class ChatFabOverlay extends StatefulWidget {
  /// Space from bottom. Default 12 = aligned with bottom navigation bar.
  final double bottomPadding;

  const ChatFabOverlay({super.key, this.bottomPadding = 12});

  @override
  State<ChatFabOverlay> createState() => _ChatFabOverlayState();
}

class _ChatFabOverlayState extends State<ChatFabOverlay> {
  bool _chatOpen = false;
  final List<_ChatBubble> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _sending = false;
  int? _conversationId;
  bool _welcomeLoaded = false;

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _toggleChat() {
    if (_chatOpen) {
      setState(() => _chatOpen = false);
      return;
    }
    _openChatWithWelcome();
  }

  Future<void> _openChatWithWelcome() async {
    setState(() {
      _chatOpen = true;
      if (!_welcomeLoaded) {
        _welcomeLoaded = true;
        _messages.clear();
        _messages.add(_ChatBubble(role: 'assistant', content: 'Hi! User'));
        _messages.add(_ChatBubble(role: 'assistant', content: 'Welcome to Personal Style Assistant'));
      }
    });
    _scrollToBottom();
    try {
      final profile = await ProfileApi.getProfile();
      if (!mounted || !_chatOpen) return;
      final name = profile.displayName;
      setState(() {
        if (_messages.length >= 2) {
          _messages[0] = _ChatBubble(role: 'assistant', content: 'Hi! $name');
        }
      });
      _scrollToBottom();
    } catch (_) {
      // Keep "Hi! User" if profile fetch fails
    }
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _sending) return;

    _controller.clear();
    setState(() {
      _messages.add(_ChatBubble(role: 'user', content: text));
      _sending = true;
    });
    _scrollToBottom();

    try {
      final res = await ChatApi.sendMessage(
        message: text,
        conversationId: _conversationId,
      );
      if (!mounted) return;
      setState(() {
        _messages.add(_ChatBubble(role: 'assistant', content: res.message));
        _conversationId = res.conversationId;
        _sending = false;
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.add(_ChatBubble(
          role: 'assistant',
          content: 'Sorry, something went wrong. ${e.toString().replaceFirst('Exception: ', '')}',
        ));
        _sending = false;
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final bottom = widget.bottomPadding;
    final right = 20.0;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        // FAB – same logo, original colors; black circle; aligned with bottom nav bar
        Positioned(
          bottom: bottom,
          right: right,
          child: Material(
            color: Colors.black,
            shape: const CircleBorder(),
            elevation: 8,
            shadowColor: Colors.black54,
            child: InkWell(
              onTap: () async {
                final token = await AuthApi.getToken();
                if (token == null || token.isEmpty) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Please log in to use chat'),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                  return;
                }
                _toggleChat();
              },
              customBorder: const CircleBorder(),
              child: SizedBox(
                width: 56,
                height: 56,
                child: ClipOval(
                  child: Image.asset(
                    'assets/icons/Chatbot_Icon.png',
                    fit: BoxFit.cover,
                    width: 56,
                    height: 56,
                  ),
                ),
              ),
            ),
          ),
        ),
        // Chat window (positioned so title is visible; sits a little above FAB)
        if (_chatOpen)
          Positioned(
            bottom: bottom + 62,
            right: right,
            child: Material(
              elevation: 16,
              shadowColor: Colors.black54,
              borderRadius: BorderRadius.circular(16),
              color: _cardBackground,
              child: Container(
                width: 320,
                height: 440,
                decoration: BoxDecoration(
                  color: _cardBackground,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Header – visible title "Personal Style Assistant"
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      decoration: BoxDecoration(
                        color: _backgroundColor,
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                        border: Border(
                          bottom: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
                        ),
                      ),
                      child: Row(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.asset(
                              'assets/icons/Chatbot_Icon.png',
                              width: 32,
                              height: 32,
                              fit: BoxFit.cover,
                            ),
                          ),
                          const SizedBox(width: 10),
                          const Expanded(
                            child: Text(
                              'Personal Style Assistant',
                              style: TextStyle(
                                color: _textPrimary,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'SpaceGrotesk',
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, color: _textSecondary, size: 24),
                            onPressed: _toggleChat,
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(minWidth: 40, minHeight: 40),
                          ),
                        ],
                      ),
                    ),
                    // Messages
                    Expanded(
                      child: ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        itemCount: _messages.length + (_sending ? 1 : 0),
                        itemBuilder: (context, index) {
                          if (index == _messages.length) {
                            return const Padding(
                              padding: EdgeInsets.symmetric(vertical: 8),
                              child: Row(
                                children: [
                                  SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: _primaryColor),
                                  ),
                                  SizedBox(width: 8),
                                  Text('Thinking...', style: TextStyle(color: _textSecondary, fontSize: 12)),
                                ],
                              ),
                            );
                          }
                          final bubble = _messages[index];
                          return _MessageBubble(role: bubble.role, content: bubble.content);
                        },
                      ),
                    ),
                    // Input
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _backgroundColor,
                        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _controller,
                              style: const TextStyle(color: _textPrimary, fontSize: 14),
                              decoration: InputDecoration(
                                hintText: 'Ask about style, outfits...',
                                hintStyle: TextStyle(color: _textSecondary.withValues(alpha: 0.7), fontSize: 14),
                                filled: true,
                                fillColor: _cardBackground,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(24),
                                  borderSide: BorderSide.none,
                                ),
                                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                              ),
                              onSubmitted: (_) => _sendMessage(),
                              maxLines: 2,
                              minLines: 1,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Material(
                            color: _primaryColor,
                            borderRadius: BorderRadius.circular(24),
                            child: InkWell(
                              onTap: _sending ? null : _sendMessage,
                              borderRadius: BorderRadius.circular(24),
                              child: const Padding(
                                padding: EdgeInsets.all(10),
                                child: Icon(Icons.send_rounded, color: Colors.black, size: 22),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _ChatBubble {
  final String role;
  final String content;

  _ChatBubble({required this.role, required this.content});
}

class _MessageBubble extends StatelessWidget {
  final String role;
  final String content;

  const _MessageBubble({required this.role, required this.content});

  @override
  Widget build(BuildContext context) {
    final isUser = role == 'user';
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) const SizedBox(width: 4),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isUser ? _primaryColor : _backgroundColor,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isUser ? 16 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 16),
                ),
              ),
              child: Text(
                content,
                style: TextStyle(
                  color: isUser ? Colors.black : _textPrimary,
                  fontSize: 14,
                  fontFamily: 'SpaceGrotesk',
                ),
              ),
            ),
          ),
          if (isUser) const SizedBox(width: 4),
        ],
      ),
    );
  }
}
