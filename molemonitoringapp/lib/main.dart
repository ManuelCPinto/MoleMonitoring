import 'package:flutter/material.dart';
import 'splash_screen.dart';
import 'bottom_nav_screen.dart';

void main() {
  runApp(const MoleMonitoringApp());
}

class MoleMonitoringApp extends StatelessWidget {
  const MoleMonitoringApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mole Monitor',
      theme: ThemeData(
        primaryColor: const Color(0xFF00BCD4),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF121212),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF00BCD4),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      initialRoute: '/splash',
      routes: {
        '/splash': (context) => const SplashScreen(),
        '/home': (context) => const BottomNavScreen(initialIndex: 0),
      },
      debugShowCheckedModeBanner: false,
    );
  }
}
