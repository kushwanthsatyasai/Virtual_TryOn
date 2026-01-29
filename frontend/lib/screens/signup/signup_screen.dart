import 'package:flutter/material.dart';
import 'dart:ui';
import 'signup_measurements_screen.dart'; // Fix the import
import '../../models/signup_draft.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  String? selectedGender;
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  static final RegExp _passwordRegex = RegExp(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$',
  );

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

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
        backgroundColor: background.withValues(alpha: 0.5),
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
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 16),
                // Name Input
                TextFormField(
                  controller: _nameController,
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
                  validator: (value) {
                    final v = (value ?? '').trim();
                    if (v.isEmpty) return 'Name is required';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // Age Input
                TextFormField(
                  controller: _ageController,
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
                  validator: (value) {
                    final v = (value ?? '').trim();
                    if (v.isEmpty) return 'Age is required';
                    final parsed = int.tryParse(v);
                    if (parsed == null) return 'Enter a valid age';
                    if (parsed < 1 || parsed > 120) return 'Enter a valid age';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // Phone Input
                TextFormField(
                  controller: _phoneController,
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
                  validator: (value) {
                    final v = (value ?? '').trim();
                    if (v.isEmpty) return 'Phone number is required';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // Email Input
                TextFormField(
                  controller: _emailController,
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
                  validator: (value) {
                    final v = (value ?? '').trim();
                    if (v.isEmpty) return 'Email is required';
                    // Basic email validation (rejects spaces, requires one '@' and a domain dot)
                    final emailRegex = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$');
                    if (!emailRegex.hasMatch(v)) return 'Enter a valid email';
                    return null;
                  },
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
                const SizedBox(height: 24),
                // Password Input
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    hintText: 'Password',
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
                    suffixIcon: IconButton(
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                      icon: Icon(
                        _obscurePassword ? Icons.visibility_off : Icons.visibility,
                        color: mutedForeground,
                      ),
                    ),
                  ),
                  style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
                  validator: (value) {
                    final v = value ?? '';
                    if (v.isEmpty) return 'Password is required';
                    if (!_passwordRegex.hasMatch(v)) {
                      return 'Min 8 chars with uppercase, lowercase, number & special char';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                // Confirm Password Input
                TextFormField(
                  controller: _confirmPasswordController,
                  obscureText: _obscureConfirmPassword,
                  decoration: InputDecoration(
                    hintText: 'Confirm Password',
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
                    suffixIcon: IconButton(
                      onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                      icon: Icon(
                        _obscureConfirmPassword ? Icons.visibility_off : Icons.visibility,
                        color: mutedForeground,
                      ),
                    ),
                  ),
                  style: const TextStyle(color: foreground, fontFamily: 'SpaceGrotesk'),
                  validator: (value) {
                    final v = value ?? '';
                    if (v.isEmpty) return 'Confirm password is required';
                    if (v != _passwordController.text) return 'Passwords do not match';
                    return null;
                  },
                ),
              ],
            ),
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
              color: background.withValues(alpha: 0.5),
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    final isValid = _formKey.currentState?.validate() ?? false;
                    if (!isValid) return;
                    if (selectedGender == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Please select a gender')),
                      );
                      return;
                    }
                    final age = int.tryParse(_ageController.text.trim());
                    if (age == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Enter a valid age')),
                      );
                      return;
                    }

                    final draft = SignupDraft(
                      name: _nameController.text.trim(),
                      age: age,
                      phone: _phoneController.text.trim(),
                      email: _emailController.text.trim(),
                      gender: selectedGender!,
                      password: _passwordController.text,
                    );
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => SignUpMeasurementsScreen(draft: draft),
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