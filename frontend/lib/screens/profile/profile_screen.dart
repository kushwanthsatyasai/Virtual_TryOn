import 'package:flutter/material.dart';
import 'dart:ui';
import '../../widgets/bottom_navigation_bar.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF121212);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);
    const textPrimary = Color(0xFFFFFFFF);
    const textSecondary = Color(0xFFA0A0A0);
    const navBackground = Color(0xFF1A1A1A);

    return Scaffold(
      backgroundColor: backgroundColor,
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Profile Header with Photo
            Stack(
            children: [
              // Profile Photo
              Container(
                height: 384, // 96 * 4 = 384
                width: double.infinity,
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: NetworkImage(
                      'https://lh3.googleusercontent.com/aida-public/AB6AXuDQGAzH0HhXcsUHfmfNeOXdCFRazNUVPFeCj_Y2nx3zZCJ6cIi-pXITSQSdwIpxzArJQ1VRbfuI8aIRr6-5ZIc3_OPRDuMoTQoAkw0Pfp9NAUnBtisSNe_FB8OQrOJxP70QnSI0p2DM0IYX1WC8Nc_yD-NFWSVFCBgcueDWS9Gy31KqHvyxyB27jEYxbzeAvBloXF0xg13MhcJbiy8fnABnlHRFAS-EwGLQLPBGAef9tskbJhSpb0mXsmQ7g-xMDqLtjn8koimXdKvb',
                    ),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              // Gradient Overlay
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
              // Change Photo Button
              Positioned(
                bottom: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: primaryColor,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.camera_alt,
                        color: Colors.black,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      const Text(
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
            ],
          ),
          
          // User Information Section
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Name and Edit Button
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Alexia Doe',
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        color: textPrimary,
                        fontFamily: 'SpaceGrotesk',
                      ),
                    ),
                    TextButton.icon(
                      onPressed: () {
                        // TODO: Navigate to edit profile
                      },
                      icon: const Icon(
                        Icons.edit,
                        color: primaryColor,
                        size: 16,
                      ),
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
                
                // Contact Information
                Column(
                  children: [
                    _buildContactInfo(
                      icon: Icons.phone,
                      label: 'Phone',
                      value: '+1 234 567 890',
                    ),
                    const SizedBox(height: 16),
                    _buildContactInfo(
                      icon: Icons.email,
                      label: 'Email',
                      value: 'alexia.doe@example.com',
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Measurements Section
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
                          _buildMeasurementCard('Height', '175 cm'),
                          _buildMeasurementCard('Weight', '62 kg'),
                          _buildMeasurementCard('Chest', '88 cm'),
                          _buildMeasurementCard('Waist', '68 cm'),
                          _buildMeasurementCard('Hips', '95 cm'),
                          _buildMeasurementCard('Inseam', '80 cm'),
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
    bottomNavigationBar: const CustomBottomNavigationBar(
      currentIndex: 3,
    ),
    );
  }

  Widget _buildContactInfo({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          color: const Color(0xFFA0A0A0),
          size: 20,
        ),
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
