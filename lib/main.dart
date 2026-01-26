import 'package:flutter/material.dart';
import 'screens/landing/splash_screen1.dart';  // Update import path

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Virtue Try On',
      theme: ThemeData(
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF06F81A),
          surface: const Color(0xFF121212),
          secondary: const Color(0xFFA0A0A0),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF06F81A),
            foregroundColor: Colors.black,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(28),
            ),
          ),
        ),
        fontFamily: 'SpaceGrotesk',
      ),
      debugShowCheckedModeBanner: false,
      home: const SplashScreen(),
    );
  }
}
