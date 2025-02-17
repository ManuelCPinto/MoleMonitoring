import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _iconScaleAnimation;
  late Animation<double> _textFadeAnimation;

  // Use your app's blue color.
  final Color accentBlue = const Color(0xFF005EB8);

  @override
  void initState() {
    super.initState();
    // Total animation duration: 3 seconds.
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );

    // Icon scales from 0 to 1 between 0% and 60% of the animation with an elastic curve.
    _iconScaleAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.6, curve: Curves.elasticOut),
      ),
    );

    // Text fades in from 0 to 1 between 60% and 100% of the animation.
    _textFadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.6, 1.0, curve: Curves.easeIn),
      ),
    );

    // Start the animations.
    _controller.forward();

    // After 3 seconds, navigate to the home screen.
    Timer(const Duration(seconds: 3), () {
      Navigator.pushReplacementNamed(context, '/home');
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Create a vertical gradient from your blue to white.
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [accentBlue, Colors.white],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Animated scaling app icon.
              ScaleTransition(
                scale: _iconScaleAnimation,
                child: Image.asset(
                  'assets/ic_launcher.png', // Ensure this asset exists in your assets folder.
                  width: 120,
                  height: 120,
                ),
              ),
              const SizedBox(height: 20),
              // Animated fade-in text.
              FadeTransition(
                opacity: _textFadeAnimation,
                child: Text(
                  "MoleMonitoring",
                  style: GoogleFonts.lato(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: accentBlue,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
