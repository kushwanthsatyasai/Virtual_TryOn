import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../models/user_profile.dart';
import '../../services/api_client.dart';
import '../../services/auth_api.dart';
import '../../services/profile_api.dart';
import '../../widgets/bottom_navigation_bar.dart';
import '../../widgets/chat_fab_overlay.dart';
import '../landing/login_screen.dart';
import 'edit_profile_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  UserProfile? _profile;
  bool _loading = true;
  String? _error;
  bool _uploadingPhoto = false;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final token = await AuthApi.getToken();
    if (token == null || token.isEmpty) {
      setState(() {
        _loading = false;
        _error = 'Not logged in';
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final profile = await ProfileApi.getProfile();
      if (mounted) {
        setState(() {
          _profile = profile;
          _loading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _profile = null;
          _loading = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  String _avatarUrl(UserProfile p) {
    final url = p.avatarUrl;
    if (url == null || url.isEmpty) return '';
    if (url.startsWith('http')) return url;
    final base = kApiBaseUrl.trim();
    final baseTrimmed = base.endsWith('/') ? base : '$base/';
    final path = url.startsWith('/') ? url.substring(1) : url;
    return '$baseTrimmed$path';
  }

  void _showChangePhotoOptions() {
    final primaryColor = const Color(0xFF06F81A);
    final textPrimary = const Color(0xFFFFFFFF);
    final textSecondary = const Color(0xFFA0A0A0);

    showModalBottomSheet<void>(
      context: context,
      backgroundColor: const Color(0xFF1E1E1E),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Change profile photo',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Choose how you want to add a new photo',
                style: TextStyle(fontSize: 14, color: textSecondary),
              ),
              const SizedBox(height: 24),
              ListTile(
                leading: Icon(Icons.camera_alt, color: primaryColor),
                title: Text('Take photo', style: TextStyle(color: textPrimary)),
                onTap: () {
                  Navigator.pop(context);
                  _pickAndUploadPhoto(ImageSource.camera);
                },
              ),
              ListTile(
                leading: Icon(Icons.photo_library, color: primaryColor),
                title: Text('Choose from gallery', style: TextStyle(color: textPrimary)),
                onTap: () {
                  Navigator.pop(context);
                  _pickAndUploadPhoto(ImageSource.gallery);
                },
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text('Cancel', style: TextStyle(color: textSecondary)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pickAndUploadPhoto(ImageSource source) async {
    final picker = ImagePicker();
    final XFile? file = await picker.pickImage(
      source: source,
      maxWidth: 1920,
      maxHeight: 1920,
      imageQuality: 85,
    );
    if (file == null || !mounted) return;

    setState(() => _uploadingPhoto = true);
    try {
      await AuthApi.uploadFullBodyPhoto(photoFile: file);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Profile photo updated'),
            backgroundColor: Color(0xFF06F81A),
            behavior: SnackBarBehavior.floating,
          ),
        );
        _loadProfile();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to upload: ${e.toString().replaceFirst('Exception: ', '')}'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _uploadingPhoto = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);

    if (_loading && _profile == null) {
      return Scaffold(
        backgroundColor: backgroundColor,
        body: const Center(
          child: CircularProgressIndicator(color: primaryColor),
        ),
        bottomNavigationBar: const CustomBottomNavigationBar(currentIndex: 3),
      );
    }

    if (_error != null && _profile == null) {
      return Scaffold(
        backgroundColor: backgroundColor,
        body: Center(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    _error!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: textSecondary, fontSize: 16),
                  ),
                  const SizedBox(height: 24),
                  if (_error == 'Not logged in')
                    FilledButton(
                      onPressed: () {
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(builder: (context) => const LoginScreen()),
                        );
                      },
                      child: const Text('Log in'),
                    ),
                ],
              ),
            ),
          ),
        ),
        bottomNavigationBar: const CustomBottomNavigationBar(currentIndex: 3),
      );
    }

    final p = _profile!;
    final avatarUrl = _avatarUrl(p);

    return Scaffold(
      backgroundColor: backgroundColor,
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Column(
              children: [
                // Profile Header with Photo
                Stack(
              children: [
                Container(
                  height: 384,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: cardBackground,
                    image: avatarUrl.isNotEmpty
                        ? DecorationImage(
                            image: NetworkImage(avatarUrl),
                            fit: BoxFit.cover,
                          )
                        : null,
                  ),
                  child: avatarUrl.isEmpty
                      ? const Center(
                          child: Icon(Icons.person, size: 80, color: textSecondary),
                        )
                      : null,
                ),
                Positioned.fill(
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withValues(alpha: 0.8),
                        ],
                      ),
                    ),
                  ),
                ),
                Positioned(
                  bottom: 16,
                  right: 16,
                  child: IgnorePointer(
                    ignoring: _uploadingPhoto,
                    child: GestureDetector(
                      onTap: _showChangePhotoOptions,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: primaryColor,
                          borderRadius: BorderRadius.circular(24),
                        ),
                        child: _uploadingPhoto
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.black,
                                ),
                              )
                            : const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.camera_alt, color: Colors.black, size: 16),
                                  SizedBox(width: 8),
                                  Text(
                                    'Change Photo',
                                    style: TextStyle(
                                      color: Colors.black,
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            // User Information Section
            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(
                        child: Text(
                          p.displayName,
                          style: const TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.bold,
                            color: textPrimary,
                            fontFamily: 'SpaceGrotesk',
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 2,
                        ),
                      ),
                      const SizedBox(width: 8),
                      TextButton.icon(
                        onPressed: () async {
                          final updated = await Navigator.of(context).push<UserProfile>(
                            MaterialPageRoute(
                              builder: (context) => EditProfileScreen(profile: p),
                            ),
                          );
                          if (updated != null) {
                            _loadProfile();
                          }
                        },
                        icon: const Icon(Icons.edit, color: primaryColor, size: 16),
                        label: const Text(
                          'Edit',
                          style: TextStyle(
                            color: primaryColor,
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Column(
                    children: [
                      _buildContactInfo(
                        icon: Icons.phone,
                        label: 'Phone',
                        value: p.phone ?? '—',
                      ),
                      const SizedBox(height: 16),
                      _buildContactInfo(
                        icon: Icons.email,
                        label: 'Email',
                        value: p.email,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Container(
                    padding: const EdgeInsets.only(top: 24),
                    decoration: BoxDecoration(
                      border: Border(
                        top: BorderSide(
                          color: Colors.white.withValues(alpha: 0.1),
                          width: 1,
                        ),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Measurements',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: textPrimary,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                        const SizedBox(height: 16),
                        GridView.count(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          crossAxisCount: 2,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                          childAspectRatio: 2.2,
                          children: [
                            _buildMeasurementCard('Height', p.heightCm != null ? '${p.heightCm!.round()} cm' : '—'),
                            _buildMeasurementCard('Weight', p.weightKg != null ? '${p.weightKg!.round()} kg' : '—'),
                            _buildMeasurementCard('Chest', p.chestCm != null ? '${p.chestCm!.round()} cm' : '—'),
                            _buildMeasurementCard('Waist', p.waistCm != null ? '${p.waistCm!.round()} cm' : '—'),
                            _buildMeasurementCard('Hips', p.hipCm != null ? '${p.hipCm!.round()} cm' : '—'),
                            _buildMeasurementCard('Inseam', p.preferredSize ?? '—'),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            ],
          ),
        ),
          const ChatFabOverlay(),
        ],
      ),
      bottomNavigationBar: const CustomBottomNavigationBar(currentIndex: 3),
    );
  }

  Widget _buildContactInfo({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFFA0A0A0), size: 20),
        const SizedBox(width: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: Color(0xFFA0A0A0),
                fontSize: 12,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
            Text(
              value,
              style: const TextStyle(
                color: Color(0xFFFFFFFF),
                fontSize: 16,
                fontWeight: FontWeight.w500,
                fontFamily: 'SpaceGrotesk',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMeasurementCard(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Color(0xFFA0A0A0),
              fontSize: 12,
              fontFamily: 'SpaceGrotesk',
            ),
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(
              color: Color(0xFFFFFFFF),
              fontSize: 16,
              fontWeight: FontWeight.bold,
              fontFamily: 'SpaceGrotesk',
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
