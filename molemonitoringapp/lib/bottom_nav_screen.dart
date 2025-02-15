import 'package:flutter/material.dart';
import 'package:salomon_bottom_bar/salomon_bottom_bar.dart';
import 'package:molemonitoringapp/screens/camera_tab.dart';
import 'package:molemonitoringapp/screens/mainscreen.dart';
import 'package:molemonitoringapp/screens/resultsscreen.dart';
import 'package:molemonitoringapp/screens/profilescreen.dart';

class BottomNavScreen extends StatefulWidget {
  const BottomNavScreen({Key? key}) : super(key: key);

  @override
  State<BottomNavScreen> createState() => _BottomNavScreenState();
}

class _BottomNavScreenState extends State<BottomNavScreen> {
  int _currentIndex = 0;

  final List<Widget> _pages = [];

  @override
  void initState() {
    super.initState();
    _pages.addAll([
      HomeScreen(onTabTapped: _onTabTapped), // Pass navigation function
      const CameraTab(),
      const ResultsScreen(),
      const ProfileScreen(),
    ]);
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    const Color primaryColor = Color(0xFF005EB8);

    return Scaffold(
      body: _pages[_currentIndex],

      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 10,
              offset: Offset(0, -1),
            ),
          ],
        ),
        child: SalomonBottomBar(
          currentIndex: _currentIndex,
          onTap: _onTabTapped,
          items: [
            SalomonBottomBarItem(
              icon: const Icon(Icons.home),
              title: const Text("Home"),
              selectedColor: primaryColor,
            ),

            // Camera (monitor)
            SalomonBottomBarItem(
              icon: Stack(
                alignment: Alignment.center,
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: primaryColor,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black26.withOpacity(0.2),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.camera_alt, color: Colors.white),
                ],
              ),
              title: const Text("Monitor"),
              selectedColor: primaryColor,
            ),

            SalomonBottomBarItem(
              icon: const Icon(Icons.bar_chart),
              title: const Text("Reports"),
              selectedColor: primaryColor,
            ),

            SalomonBottomBarItem(
              icon: const Icon(Icons.person),
              title: const Text("Profile"),
              selectedColor: primaryColor,
            ),
          ],
        ),
      ),
    );
  }
}
