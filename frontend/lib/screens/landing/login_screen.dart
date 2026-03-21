import 'package:dio/dio.dart';
import 'dart:async';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:google_sign_in_web/web_only.dart' as gsi_web;

import '../../services/auth_api.dart';
import '../home/home_screen.dart';
import '../signup/signup_screen.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  bool _obscurePassword = true;
  static bool _googleInitialized = false;

  StreamSubscription<GoogleSignInAuthenticationEvent>? _googleAuthSub;
  Future<void>? _googleWebInitFuture;

  @override
  void initState() {
    super.initState();

    if (kIsWeb) {
      _googleWebInitFuture = _initGoogleWeb();
      _googleAuthSub = GoogleSignIn.instance.authenticationEvents.listen(
        (event) async {
          if (!mounted) return;
          if (event is GoogleSignInAuthenticationEventSignIn) {
            await _handleGoogleAccount(event.user);
          }
        },
      );
    }
  }

  Future<void> _initGoogleWeb() async {
    const clientId = String.fromEnvironment(
      'GOOGLE_SIGNIN_CLIENT_ID',
      defaultValue: '',
    );
    if (!_googleInitialized) {
      await GoogleSignIn.instance.initialize(
        // For web, plugin reads this or falls back to the HTML meta tag.
        clientId: clientId.isEmpty ? null : clientId,
      );
      _googleInitialized = true;
    }
  }

  Future<void> _handleGoogleAccount(GoogleSignInAccount account) async {
    if (_loading) return;
    setState(() => _loading = true);

    try {
      final email = account.email;
      final fullName = account.displayName ?? '';
      final googleId = account.id;
      final auth = account.authentication;

      final result = await AuthApi.googleLogin(
        email: email,
        fullName: fullName,
        googleId: googleId,
        idToken: auth.idToken,
      );

      if (!mounted) return;
      if (result.needsSignup) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => SignUpScreen(
              initialName: result.fullName,
              initialEmail: result.email,
            ),
          ),
        );
      } else {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (context) => const HomeScreen()),
          (route) => false,
        );
      }
    } on DioException catch (e) {
      final msg = e.response?.data is Map &&
              (e.response?.data as Map)['detail'] != null
          ? (e.response?.data as Map)['detail'].toString()
          : (e.message ?? 'Google sign-in failed');
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

  Future<void> _signInWithGoogle() async {
    try {
      // google_sign_in v7+: use the singleton instance + `authenticate`.
      if (!_googleInitialized) {
        const clientId = String.fromEnvironment(
          'GOOGLE_SIGNIN_CLIENT_ID',
          defaultValue: '',
        );
        await GoogleSignIn.instance.initialize(
          // For web: plugin reads this or falls back to the HTML meta tag.
          clientId: clientId.isEmpty ? null : clientId,
        );
        _googleInitialized = true;
      }
      final account = await GoogleSignIn.instance.authenticate(
        scopeHint: const <String>['email', 'profile'],
      );
      await _handleGoogleAccount(account);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  void dispose() {
    _googleAuthSub?.cancel();
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
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: onSurfaceVariant,
                            size: 22,
                          ),
                          onPressed: () {
                            setState(() => _obscurePassword = !_obscurePassword);
                          },
                        ),
                      ),
                      style: const TextStyle(
                          color: onSurface, fontFamily: 'SpaceGrotesk'),
                      obscureText: _obscurePassword,
                      textInputAction: TextInputAction.done,
                      onSubmitted: (_) => _signIn(),
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const ForgotPasswordScreen(),
                            ),
                          );
                        },
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
                    if (kIsWeb)
                      FutureBuilder<void>(
                        future: _googleWebInitFuture,
                        builder: (context, snapshot) {
                          if (snapshot.connectionState != ConnectionState.done) {
                            return SizedBox(
                              width: double.infinity,
                              height: 56,
                              child: Center(
                                child: SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: CircularProgressIndicator(
                                    color: primary,
                                    strokeWidth: 2,
                                  ),
                                ),
                              ),
                            );
                          }
                          return SizedBox(
                            width: double.infinity,
                            height: 56,
                            child: gsi_web.renderButton(
                            configuration: gsi_web.GSIButtonConfiguration(
                              type: gsi_web.GSIButtonType.standard,
                              size: gsi_web.GSIButtonSize.large,
                              shape: gsi_web.GSIButtonShape.rectangular,
                              text: gsi_web.GSIButtonText.signinWith,
                              theme: gsi_web.GSIButtonTheme.filledBlue,
                            ),
                            ),
                          );
                        },
                      )
                    else
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
                            foregroundColor: onSurface,
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
                          onPressed: _loading ? null : _signInWithGoogle,
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