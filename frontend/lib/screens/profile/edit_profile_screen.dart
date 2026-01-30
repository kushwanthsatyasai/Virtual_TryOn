import 'package:flutter/material.dart';

import '../../models/user_profile.dart';
import '../../services/profile_api.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key, required this.profile});

  final UserProfile profile;

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  late final TextEditingController _nameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _ageController;
  late final TextEditingController _heightController;
  late final TextEditingController _weightController;
  late final TextEditingController _chestController;
  late final TextEditingController _waistController;
  late final TextEditingController _hipController;

  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final p = widget.profile;
    _nameController = TextEditingController(text: p.fullName ?? '');
    _phoneController = TextEditingController(text: p.phone ?? '');
    _ageController = TextEditingController(text: p.age?.toString() ?? '');
    _heightController = TextEditingController(text: p.heightCm?.toString() ?? '');
    _weightController = TextEditingController(text: p.weightKg?.toString() ?? '');
    _chestController = TextEditingController(text: p.chestCm?.toString() ?? '');
    _waistController = TextEditingController(text: p.waistCm?.toString() ?? '');
    _hipController = TextEditingController(text: p.hipCm?.toString() ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _chestController.dispose();
    _waistController.dispose();
    _hipController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() {
      _error = null;
      _loading = true;
    });
    try {
      final payload = <String, dynamic>{};
      final name = _nameController.text.trim();
      if (name.isNotEmpty) payload['full_name'] = name;
      final phone = _phoneController.text.trim();
      if (phone.isNotEmpty) payload['phone'] = phone;
      final ageStr = _ageController.text.trim();
      if (ageStr.isNotEmpty) {
        final age = int.tryParse(ageStr);
        if (age != null) payload['age'] = age;
      }
      final heightStr = _heightController.text.trim();
      if (heightStr.isNotEmpty) {
        final v = double.tryParse(heightStr);
        if (v != null) payload['height_cm'] = v;
      }
      final weightStr = _weightController.text.trim();
      if (weightStr.isNotEmpty) {
        final v = double.tryParse(weightStr);
        if (v != null) payload['weight_kg'] = v;
      }
      final chestStr = _chestController.text.trim();
      if (chestStr.isNotEmpty) {
        final v = double.tryParse(chestStr);
        if (v != null) payload['chest_cm'] = v;
      }
      final waistStr = _waistController.text.trim();
      if (waistStr.isNotEmpty) {
        final v = double.tryParse(waistStr);
        if (v != null) payload['waist_cm'] = v;
      }
      final hipStr = _hipController.text.trim();
      if (hipStr.isNotEmpty) {
        final v = double.tryParse(hipStr);
        if (v != null) payload['hip_cm'] = v;
      }

      final updated = await ProfileApi.updateProfile(payload);
      if (mounted) {
        Navigator.of(context).pop(updated);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceFirst('Exception: ', '');
          _loading = false;
        });
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textPrimary),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text(
          'Edit Profile',
          style: TextStyle(
            color: textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.bold,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        actions: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: Center(
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2, color: primaryColor),
                ),
              ),
            )
          else
            TextButton(
              onPressed: _save,
              child: const Text('Save', style: TextStyle(color: primaryColor, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 14)),
              ),
              const SizedBox(height: 16),
            ],
            _buildField('Full name', _nameController, keyboardType: TextInputType.name),
            const SizedBox(height: 16),
            _buildField('Phone', _phoneController, keyboardType: TextInputType.phone),
            const SizedBox(height: 16),
            _buildField('Age', _ageController, keyboardType: TextInputType.number),
            const SizedBox(height: 24),
            const Text(
              'Measurements (cm / kg)',
              style: TextStyle(
                color: textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w600,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
            const SizedBox(height: 12),
            _buildField('Height (cm)', _heightController, keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            _buildField('Weight (kg)', _weightController, keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            _buildField('Chest (cm)', _chestController, keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            _buildField('Waist (cm)', _waistController, keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            _buildField('Hips (cm)', _hipController, keyboardType: TextInputType.number),
          ],
        ),
      ),
    );
  }

  Widget _buildField(String label, TextEditingController controller, {TextInputType? keyboardType}) {
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: textSecondary,
            fontSize: 12,
            fontFamily: 'SpaceGrotesk',
          ),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          style: const TextStyle(color: textPrimary, fontSize: 16),
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF1E1E1E),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          ),
        ),
      ],
    );
  }
}
