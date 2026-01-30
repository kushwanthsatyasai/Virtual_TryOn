import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../services/auth_api.dart';
import '../home/home_screen.dart';
import '../signup/signup_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (username.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter email or username')),
      );
      return;
    }
    if (password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter password')),
      );
      return;
    }

    if (_loading) return;
    setState(() => _loading = true);

    try {
      await AuthApi.login(username, password);
      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const HomeScreen()),
        (route) => false,
      );
    } on DioException catch (e) {
      final msg = e.response?.data is Map &&
              (e.response?.data as Map)['detail'] != null
          ? (e.response?.data as Map)['detail'].toString()
          : (e.message ?? 'Sign in failed');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    const background = Color(0xFF0D0D0D);
    const surface = Color(0xFF1A1A1A);
    const primary = Color(0xFF39FF14);
    const onSurface = Colors.white;
    const onSurfaceVariant = Color(0xFFA3A3A3);

    return Scaffold(
      backgroundColor: background,
      body: SafeArea(
        child: Column(
          children: [
            // Header with back button
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: onSurface),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(height: 32),
                    const Text(
                      'Welcome Back',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: onSurface,
                        fontFamily: 'SpaceGrotesk',
                        letterSpacing: -1,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Sign in to continue your virtual style journey.',
                      style: TextStyle(
                        color: onSurfaceVariant,
                        fontSize: 16,
                        fontFamily: 'SpaceGrotesk',
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    TextField(
                      controller: _usernameController,
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: surface,
                        hintText: 'Email or username',
                        hintStyle: const TextStyle(color: onSurfaceVariant),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: primary),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 18, horizontal: 16),
                      ),
                      style: const TextStyle(
                          color: onSurface, fontFamily: 'SpaceGrotesk'),
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _passwordController,
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: surface,
                        hintText: 'Password',
                        hintStyle: const TextStyle(color: onSurfaceVariant),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: primary),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 18, horizontal: 16),
                      ),
                      style: const TextStyle(
                          color: onSurface, fontFamily: 'SpaceGrotesk'),
                      obscureText: true,
                      textInputAction: TextInputAction.done,
                      onSubmitted: (_) => _signIn(),
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () {},
                        child: const Text(
                          'Forgot password?',
                          style: TextStyle(
                            color: onSurfaceVariant,
                            fontWeight: FontWeight.w500,
                            fontSize: 14,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: primary,
                          foregroundColor: Colors.black,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          textStyle: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                        onPressed: _loading ? null : _signIn,
                        child: _loading
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.black,
                                ),
                              )
                            : const Text('Sign In'),
                      ),
                    ),
                    const SizedBox(height: 24),
                    // OR divider
                    Row(
                      children: [
                        Expanded(child: Divider(color: surface)),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 12),
                          child: Text(
                            'OR',
                            style: TextStyle(
                              color: onSurfaceVariant,
                              fontSize: 14,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
                        ),
                        Expanded(child: Divider(color: surface)),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Google Sign In button
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                        child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          side: BorderSide(color: surface),
                          shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          ),
                          foregroundColor: onSurface, // Added for text color
                          textStyle: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                        icon: SvgPicture.asset(
                          'assets/icons/google_logo.svg',
                          width: 24,
                          height: 24,
                        ),
                        label: const Text('Sign in with Google'),
                        onPressed: () {
                          // TODO: Implement Google sign in
                        },
                      ),
                    ),
                    const SizedBox(height: 32),
                    // Sign up link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Don't have an account? ",
                          style: TextStyle(
                            color: onSurfaceVariant,
                            fontSize: 14,
                            fontFamily: 'SpaceGrotesk',
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(builder: (context) => const SignUpScreen()),
                            );
                          },
                          child: const Text(
                            'Sign up',
                            style: TextStyle(
                              color: primary,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                              fontFamily: 'SpaceGrotesk',
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}