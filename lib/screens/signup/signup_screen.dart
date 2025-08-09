import 'package:flutter/material.dart';
import 'dart:ui';
import 'signup_measurements_screen.dart'; // Fix the import

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  String? selectedGender;

  @override
  Widget build(BuildContext context) {
    // Colors matching the HTML/CSS variables
    const background = Color(0xFF000000);
    const foreground = Color(0xFFF8F8F8);
    const primary = Color(0xFF06F81A);
    const primaryForeground = Color(0xFF000000);
    const muted = Color(0xFF1A1A1A);
    const mutedForeground = Color(0xFFA3A3A3);

    return Scaffold(
      backgroundColor: background,
      // Sticky Header
      appBar: AppBar(
        backgroundColor: background.withOpacity(0.5),
        flexibleSpace: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(color: Colors.transparent),
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: foreground),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Sign Up',
          style: TextStyle(
            color: foreground,
            fontSize: 20,
            fontWeight: FontWeight.bold,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 16),
              // Name Input
              TextField(
                decoration: InputDecoration(
                  hintText: 'Name',
                  hintStyle: const TextStyle(color: mutedForeground),
                  filled: true,
                  fillColor: muted,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primary, width: 2),
                  ),
                  contentPadding: const EdgeInsets.all(16),
                ),
                style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
              ),
              const SizedBox(height: 16),
              // Age Input
              TextField(
                decoration: InputDecoration(
                  hintText: 'Age',
                  hintStyle: const TextStyle(color: mutedForeground),
                  filled: true,
                  fillColor: muted,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primary, width: 2),
                  ),
                  contentPadding: const EdgeInsets.all(16),
                ),
                keyboardType: TextInputType.number,
                style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
              ),
              const SizedBox(height: 16),
              // Phone Input
              TextField(
                decoration: InputDecoration(
                  hintText: 'Phone Number',
                  hintStyle: const TextStyle(color: mutedForeground),
                  filled: true,
                  fillColor: muted,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primary, width: 2),
                  ),
                  contentPadding: const EdgeInsets.all(16),
                ),
                keyboardType: TextInputType.phone,
                style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
              ),
              const SizedBox(height: 16),
              // Email Input
              TextField(
                decoration: InputDecoration(
                  hintText: 'Email',
                  hintStyle: const TextStyle(color: mutedForeground),
                  filled: true,
                  fillColor: muted,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primary, width: 2),
                  ),
                  contentPadding: const EdgeInsets.all(16),
                ),
                keyboardType: TextInputType.emailAddress,
                style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
              ),
              const SizedBox(height: 24),
              // Gender Selection
              const Text(
                'Gender',
                style: TextStyle(
                  color: foreground,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  fontFamily: 'SpaceGrotesk',
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _buildGenderButton('Male', selectedGender == 'male', () {
                    setState(() => selectedGender = 'male');
                  }),
                  const SizedBox(width: 12),
                  _buildGenderButton('Female', selectedGender == 'female', () {
                    setState(() => selectedGender = 'female');
                  }),
                  const SizedBox(width: 12),
                  _buildGenderButton('Other', selectedGender == 'other', () {
                    setState(() => selectedGender = 'other');
                  }),
                ],
              ),
            ],
          ),
        ),
      ),
      // Sticky Footer
      bottomNavigationBar: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: background.withOpacity(0.5),
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const SignUpMeasurementsScreen(),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primary,
                    foregroundColor: primaryForeground,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'SpaceGrotesk',
                    ),
                  ),
                  child: const Text('Next'),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGenderButton(String label, bool isSelected, VoidCallback onTap) {
    const primary = Color(0xFF06F81A);
    const muted = Color(0xFF1A1A1A);
    const mutedForeground = Color(0xFFA3A3A3);
    const primaryForeground = Color(0xFF000000);

    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          height: 48,
          decoration: BoxDecoration(
            color: isSelected ? primary : Colors.transparent,
            border: Border.all(
              color: isSelected ? primary : muted,
              width: 2,
            ),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: isSelected ? primaryForeground : mutedForeground,
                fontSize: 16,
                fontWeight: FontWeight.w500,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
          ),
        ),
      ),
    );
  }
}