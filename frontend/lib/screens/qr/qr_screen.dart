import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:ui';

class QRScreen extends StatefulWidget {
  const QRScreen({super.key});

  @override
  State<QRScreen> createState() => _QRScreenState();
}

class _QRScreenState extends State<QRScreen> with SingleTickerProviderStateMixin {
  late MobileScannerController controller;
  late AnimationController _beamController;
  String statusText = 'Starting camera...';

  @override
  void initState() {
    super.initState();
    controller = MobileScannerController();
    _beamController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
    _requestCameraPermission();
  }

  Future<void> _requestCameraPermission() async {
    final status = await Permission.camera.request();
    if (status.isDenied) {
      setState(() {
        statusText = 'Camera access denied. Please allow camera permissions.';
      });
    } else {
      setState(() {
        statusText = 'Camera active. Point at QR code.';
      });
    }
  }

  @override
  void dispose() {
    controller.dispose();
    _beamController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const backgroundColor = Color(0xFF000000);
    const primaryColor = Color(0xFF06F81A);
    const cardBackground = Color(0xFF1E1E1E);

    return Scaffold(
      backgroundColor: backgroundColor,
      body: Column(
        children: [
          // Header - matches qr.html exactly
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.5),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Close button (X)
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(
                    Icons.close,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                // Title
                const Text(
                  'Scan QR Code',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'SpaceGrotesk',
                  ),
                ),
                // Spacer to balance layout
                const SizedBox(width: 24),
              ],
            ),
          ),

          // Main content - centered scanner container
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Scanner container with dashed border - matches qr.html
                Container(
                  width: 256, // 64 * 4 = 256
                  height: 256,
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: primaryColor,
                      width: 4,
                      style: BorderStyle.solid,
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Stack(
                      children: [
                        // Camera view
                        MobileScanner(
                          controller: controller,
                          onDetect: (capture) {
                            final List<Barcode> barcodes = capture.barcodes;
                            for (final barcode in barcodes) {
                              _handleQRCode(barcode.rawValue ?? '');
                            }
                          },
                        ),
                        // Scanner beam animation
                        AnimatedBuilder(
                          animation: _beamController,
                          builder: (context, child) {
                            return Positioned(
                              top: _beamController.value * 256,
                              left: 0,
                              right: 0,
                              child: Container(
                                height: 2,
                                decoration: BoxDecoration(
                                  color: primaryColor,
                                  boxShadow: [
                                    BoxShadow(
                                      color: primaryColor.withValues(alpha: 0.5),
                                      blurRadius: 8,
                                      spreadRadius: 2,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),

                // Status text
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(
                    statusText,
                    style: const TextStyle(
                      color: Color(0xFFA0A0A0),
                      fontSize: 14,
                      fontFamily: 'SpaceGrotesk',
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),

          // Footer - matches qr.html exactly
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardBackground,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: backgroundColor,
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: const BorderSide(
                    color: Color(0xFF404040),
                    width: 1,
                  ),
                ),
              ),
              onPressed: _pickFromGallery,
              icon: Icon(
                Icons.photo_library_outlined,
                color: primaryColor,
                size: 24,
              ),
              label: const Text(
                'Access from Gallery',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  fontFamily: 'SpaceGrotesk',
                ),
              ),
            ),
          ),


        ],
      ),
    );
  }

  Future<void> _pickFromGallery() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        statusText = 'Processing image...';
      });
      // TODO: Implement QR code detection from image
    }
  }

  void _handleQRCode(String data) {
    if (data.startsWith('http://') || data.startsWith('https://')) {
      setState(() {
        statusText = 'URL detected: $data';
      });
    } else {
      setState(() {
        statusText = 'QR Code content: $data';
      });
    }
  }


}