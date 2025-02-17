import 'package:flutter/material.dart';
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
        primaryColor: Color(0xFF00BCD4),
        appBarTheme: AppBarTheme(
          backgroundColor: Color(0xFF121212),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFF00BCD4),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      home: const BottomNavScreen(),
    );
  }
}
