import 'package:flutter/material.dart';
import 'dart:ui';
import 'signup_upload_photo_screen.dart';
import '../../models/signup_draft.dart';

class SignUpMeasurementsScreen extends StatefulWidget {
  const SignUpMeasurementsScreen({super.key, required this.draft});

  final SignupDraft draft;

  @override
  State<SignUpMeasurementsScreen> createState() => _SignUpMeasurementsScreenState();
}

class _SignUpMeasurementsScreenState extends State<SignUpMeasurementsScreen> {
  final _formKey = GlobalKey<FormState>();

  final _chestController = TextEditingController();
  final _waistController = TextEditingController();
  final _heightFeetController = TextEditingController();
  final _heightInchesController = TextEditingController();
  final _weightController = TextEditingController();

  @override
  void dispose() {
    _chestController.dispose();
    _waistController.dispose();
    _heightFeetController.dispose();
    _heightInchesController.dispose();
    _weightController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const background = Color(0xFF000000);
    const foreground = Color(0xFFFFFFFF);
    const primary = Color(0xFF06F81A);
    const primaryForeground = Color(0xFF000000);
    const gray400 = Color(0xFFA3A3A3);
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
                  // Actions (Skip + Close)
                  Row(
                    children: [
                      TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => SignUpUploadPhotoScreen(
                                draft: widget.draft.copyWith(clearMeasurements: true),
                              ),
                            ),
                          );
                        },
                        child: const Text(
                          'Skip',
                          style: TextStyle(
                            color: primary,
                            fontFamily: 'SpaceGrotesk',
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: foreground),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
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
                      _buildMeasurementField(
                        label: 'Chest',
                        unit: 'in',
                        controller: _chestController,
                      ),
                      const SizedBox(height: 24),
                      _buildMeasurementField(
                        label: 'Waist',
                        unit: 'in',
                        controller: _waistController,
                      ),
                      const SizedBox(height: 24),
                      _buildHeightField(),
                      const SizedBox(height: 24),
                      _buildMeasurementField(
                        label: 'Weight',
                        unit: 'lbs',
                        controller: _weightController,
                      ),
                    ],
                  ),
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
                    final ok = _formKey.currentState?.validate() ?? false;
                    if (!ok) return;

                    final chest = double.tryParse(_chestController.text.trim());
                    final waist = double.tryParse(_waistController.text.trim());
                    final heightFt = int.tryParse(_heightFeetController.text.trim());
                    final heightIn = int.tryParse(_heightInchesController.text.trim());
                    final weight = double.tryParse(_weightController.text.trim());

                    if (chest == null || waist == null || heightFt == null || heightIn == null || weight == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Please enter valid measurements')),
                      );
                      return;
                    }

                    final updated = widget.draft.copyWith(
                      chestIn: chest,
                      waistIn: waist,
                      heightFeet: heightFt,
                      heightInches: heightIn,
                      weightLbs: weight,
                    );

                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => SignUpUploadPhotoScreen(draft: updated),
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

  Widget _buildMeasurementField({
    required String label,
    required String unit,
    required TextEditingController controller,
  }) {
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
            TextFormField(
              controller: controller,
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
              validator: (value) {
                final v = (value ?? '').trim();
                if (v.isEmpty) return 'Required';
                final parsed = double.tryParse(v);
                if (parsed == null) return 'Invalid';
                if (parsed <= 0) return 'Invalid';
                return null;
              },
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

  Widget _buildHeightField() {
    const gray300 = Color(0xFFD4D4D4);
    const gray400 = Color(0xFFA3A3A3);
    const secondary = Color(0xFF1E1E1E);
    const primary = Color(0xFF06F81A);

    InputDecoration decoration(String hint) {
      return InputDecoration(
        hintText: hint,
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
        contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Height',
          style: TextStyle(
            color: gray300,
            fontSize: 14,
            fontWeight: FontWeight.w500,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _heightFeetController,
                textAlign: TextAlign.center,
                keyboardType: TextInputType.number,
                decoration: decoration('ft'),
                style: const TextStyle(color: gray300, fontSize: 16, fontFamily: 'SpaceGrotesk'),
                validator: (value) {
                  final v = (value ?? '').trim();
                  if (v.isEmpty) return 'Required';
                  final parsed = int.tryParse(v);
                  if (parsed == null) return 'Invalid';
                  if (parsed <= 0 || parsed > 8) return 'Invalid';
                  return null;
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TextFormField(
                controller: _heightInchesController,
                textAlign: TextAlign.center,
                keyboardType: TextInputType.number,
                decoration: decoration('in'),
                style: const TextStyle(color: gray300, fontSize: 16, fontFamily: 'SpaceGrotesk'),
                validator: (value) {
                  final v = (value ?? '').trim();
                  if (v.isEmpty) return 'Required';
                  final parsed = int.tryParse(v);
                  if (parsed == null) return 'Invalid';
                  if (parsed < 0 || parsed > 11) return 'Invalid';
                  return null;
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}