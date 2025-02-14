import 'package:flutter/material.dart';
import 'bottom_nav_screen.dart';
import 'package:google_fonts/google_fonts.dart';

void main() {
  runApp(const MoleMonitoringApp());
}

class MoleMonitoringApp extends StatelessWidget {
  const MoleMonitoringApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mole Monitor',
      theme: ThemeData(
        primaryColor: Color(0xFF00BCD4), // Cyan
        //scaffoldBackgroundColor: Colors.pink, // Midnight Blue
        appBarTheme: AppBarTheme(
          backgroundColor: Color(0xFF121212), // Dark background
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFF00BCD4), // Cyan buttons
            //foregroundColor: Colors.green, // Dark text/icons
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
