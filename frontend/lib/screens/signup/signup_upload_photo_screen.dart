import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io' show File;

import '../../models/signup_draft.dart';
import '../../services/auth_api.dart';
import '../home/home_screen.dart';

class SignUpUploadPhotoScreen extends StatefulWidget {
  const SignUpUploadPhotoScreen({super.key, required this.draft});

  final SignupDraft draft;

  @override
  State<SignUpUploadPhotoScreen> createState() => _SignUpUploadPhotoScreenState();
}

class _SignUpUploadPhotoScreenState extends State<SignUpUploadPhotoScreen> {
  bool _loading = false;
  XFile? _picked;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final file = await picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 90,
    );
    if (!mounted) return;
    if (file != null) setState(() => _picked = file);
  }

  Future<void> _completeSignup({required bool uploadPhoto}) async {
    if (_loading) return;
    setState(() => _loading = true);
    try {
      final token = await AuthApi.register(widget.draft.toRegisterPayload());

      if (uploadPhoto && _picked != null) {
        // On web, use the picked file bytes directly; on mobile/desktop, compress first.
        if (kIsWeb) {
          await AuthApi.uploadFullBodyPhoto(photoFile: _picked!, token: token);
        } else {
          final compressed = await FlutterImageCompress.compressWithFile(
            _picked!.path,
            minWidth: 512,
            minHeight: 512,
            quality: 80,
          );

          final bytes = compressed ?? await _picked!.readAsBytes();

          await AuthApi.uploadFullBodyPhotoBytes(
            bytes: bytes,
            filename: _picked!.name,
            token: token,
          );
        }
      }

      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const HomeScreen()),
        (route) => false,
      );
    } on DioException catch (e) {
      final msg = e.response?.data is Map && (e.response?.data as Map)['detail'] != null
          ? (e.response?.data as Map)['detail'].toString()
          : (e.message ?? 'Signup failed');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Colors
    const brandGreen = Color(0xFF06F81A);
    const backgroundDark = Color(0xFF101110);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);
    const containerBg = Color(0xFF1A1C1A);
    const borderColor = Color(0xFF272927);

    return Scaffold(
      backgroundColor: backgroundDark,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(56),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back, color: textPrimary),
                      onPressed: () => Navigator.pop(context),
                    ),
                    TextButton(
                      onPressed: _loading ? null : () => _completeSignup(uploadPhoto: false),
                      child: const Text(
                        'Skip',
                        style: TextStyle(
                          color: brandGreen,
                          fontFamily: 'SpaceGrotesk',
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
                // Progress indicators
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: List.generate(
                    3,
                    (index) => Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2),
                      child: Container(
                        width: 40,
                        height: 6,
                        decoration: BoxDecoration(
                          color: brandGreen,
                          borderRadius: BorderRadius.circular(3),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
            const SizedBox(height: 24),
            const Text(
              'One last step...',
              style: TextStyle(
                color: textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Upload a full-body photo for the best virtual try-on experience.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: textSecondary,
                fontSize: 16,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
            const SizedBox(height: 40),
            GestureDetector(
              onTap: _loading ? null : _pickImage,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 24),
                decoration: BoxDecoration(
                  color: containerBg,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: borderColor,
                    width: 2,
                    style: BorderStyle.solid,
                  ),
                ),
                child: _picked == null
                    ? const Column(
                        children: [
                          SizedBox(height: 16),
                          _UploadIcon(),
                          SizedBox(height: 16),
                          Text(
                            'Tap to upload a photo',
                            style: TextStyle(
                              color: Color(0xFFFFFFFF),
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'PNG, JPG, or HEIC',
                            style: TextStyle(
                              color: Color(0xFFA0A0A0),
                              fontSize: 12,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
                          SizedBox(height: 16),
                        ],
                      )
                    : Column(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(20),
                            child: kIsWeb
                                ? Image.network(
                                    _picked!.path,
                                    height: 220,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                  )
                                : Image.file(
                                    File(_picked!.path),
                                    height: 220,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                  ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _picked!.name,
                            style: const TextStyle(
                              color: Color(0xFFA0A0A0),
                              fontSize: 12,
                              fontFamily: 'SpaceGrotesk',
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 24),
            _buildTip('Ensure your entire body is visible in the photo.'),
            const SizedBox(height: 8),
            _buildTip('Use a well-lit photo with a neutral background.'),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _loading
                    ? null
                    : () => _completeSignup(uploadPhoto: _picked != null),
                style: ElevatedButton.styleFrom(
                  backgroundColor: brandGreen,
                  foregroundColor: backgroundDark,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'SpaceGrotesk',
                  ),
                ),
                child: _loading
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Sign Up'),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
        ),
      ),
    );
  }
}

Widget _buildTip(String text) {
  return Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      const Icon(
        Icons.check_circle,
        color: Color(0xFF06F81A),
        size: 20,
      ),
      const SizedBox(width: 8),
      Expanded(
        child: Text(
          text,
          style: const TextStyle(
            color: Color(0xFFA0A0A0),
            fontSize: 14,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
      ),
    ],
  );
}

class _UploadIcon extends StatelessWidget {
  const _UploadIcon();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 64,
      height: 64,
      decoration: const BoxDecoration(
        color: Color(0xFF272927),
        shape: BoxShape.circle,
      ),
      child: const Icon(
        Icons.cloud_upload_outlined,
        color: Color(0xFF06F81A),
        size: 32,
      ),
    );
  }
}