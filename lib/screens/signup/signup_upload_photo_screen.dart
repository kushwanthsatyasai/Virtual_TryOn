import 'package:flutter/material.dart';
import 'dart:ui';
import '../home/home_screen.dart'; // Import the HomeScreen
class SignUpUploadPhotoScreen extends StatelessWidget {
  const SignUpUploadPhotoScreen({super.key});

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
                      onPressed: () {
                        // TODO: Implement skip functionality
                      },
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
        child: Column(
          children: [
            const Spacer(flex: 1),
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
            // Upload container
            GestureDetector(
              onTap: () {
                // TODO: Implement image picker
              },
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 40),
                decoration: BoxDecoration(
                  color: containerBg,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: borderColor,
                    width: 2,
                    style: BorderStyle.solid,
                  ),
                ),
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: const BoxDecoration(
                        color: borderColor,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.cloud_upload_outlined,
                        color: brandGreen,
                        size: 32,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Tap to upload a photo',
                      style: TextStyle(
                        color: textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'PNG, JPG, or HEIC',
                      style: TextStyle(
                        color: textSecondary,
                        fontSize: 12,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            // Tips
            _buildTip('Ensure your entire body is visible in the photo.'),
            const SizedBox(height: 8),
            _buildTip('Use a well-lit photo with a neutral background.'),
            const Spacer(flex: 2),
            // Finish button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () {
                  // Navigate to home screen and remove all previous routes
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (context) => const HomeScreen()),
                    (route) => false,
                  );
                },
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
                child: const Text('Sign Up'),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
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
}