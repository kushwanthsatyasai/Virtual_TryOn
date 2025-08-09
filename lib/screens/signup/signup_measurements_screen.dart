import 'package:flutter/material.dart';
import 'dart:ui';
import 'signup_upload_photo_screen.dart';

class SignUpMeasurementsScreen extends StatelessWidget {
  const SignUpMeasurementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const background = Color(0xFF000000);
    const foreground = Color(0xFFFFFFFF);
    const primary = Color(0xFF06F81A);
    const primaryForeground = Color(0xFF000000);
    const secondary = Color(0xFF1E1E1E);
    const gray300 = Color(0xFFD4D4D4);
    const gray400 = Color(0xFFA3A3A3);
    const gray500 = Color(0xFF737373);
    const zinc700 = Color(0xFF3F3F46);

    return Scaffold(
      backgroundColor: background,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Progress Indicator
                  Row(
                    children: [
                      Container(
                        width: 32,
                        height: 4,
                        decoration: BoxDecoration(
                          color: zinc700,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        width: 32,
                        height: 4,
                        decoration: BoxDecoration(
                          color: primary,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        width: 32,
                        height: 4,
                        decoration: BoxDecoration(
                          color: zinc700,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ],
                  ),
                  // Close Button
                  IconButton(
                    icon: const Icon(Icons.close, color: foreground),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'What are your measurements?',
                      style: TextStyle(
                        color: foreground,
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'This helps us find the perfect fit for you.',
                      style: TextStyle(
                        color: gray400,
                        fontSize: 16,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                    const SizedBox(height: 32),
                    _buildMeasurementField('Chest', 'in'),
                    const SizedBox(height: 24),
                    _buildMeasurementField('Waist', 'in'),
                    const SizedBox(height: 24),
                    _buildMeasurementField('Height', 'ft/in'),
                    const SizedBox(height: 24),
                    _buildMeasurementField('Weight', 'lbs'),
                  ],
                ),
              ),
            ),
            // Footer
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const SignUpUploadPhotoScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primary,
                    foregroundColor: primaryForeground,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'SpaceGrotesk',
                    ),
                  ),
                  child: const Text('Next'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMeasurementField(String label, String unit) {
    const gray300 = Color(0xFFD4D4D4);
    const gray400 = Color(0xFFA3A3A3);
    const secondary = Color(0xFF1E1E1E);
    const primary = Color(0xFF06F81A);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: gray300,
            fontSize: 14,
            fontWeight: FontWeight.w500,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        const SizedBox(height: 8),
        Stack(
          children: [
            TextField(
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                hintText: '0',
                hintStyle: const TextStyle(color: gray400),
                filled: true,
                fillColor: secondary,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: primary),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  vertical: 16,
                  horizontal: 16,
                ),
              ),
              style: const TextStyle(
                color: gray300,
                fontSize: 16,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
            Positioned(
              right: 16,
              top: 0,
              bottom: 0,
              child: Center(
                child: Text(
                  unit,
                  style: const TextStyle(
                    color: gray400,
                    fontSize: 14,
                    fontFamily: 'SpaceGrotesk',
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}