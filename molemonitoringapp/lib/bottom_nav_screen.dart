import 'package:flutter/material.dart';
import 'package:salomon_bottom_bar/salomon_bottom_bar.dart';
import 'package:molemonitoringapp/screens/camera_tab.dart';
import 'package:molemonitoringapp/screens/mainscreen.dart';
import 'package:molemonitoringapp/screens/resultsscreen.dart';
import 'package:molemonitoringapp/screens/profilescreen.dart';

class BottomNavScreen extends StatefulWidget {
  const BottomNavScreen({super.key});

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
      HomeScreen(onTabTapped: _onTabTapped),
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

  Widget _buildBubbleIcon(IconData icon, bool isSelected) {
    const Color primaryColor = Color(0xFF005EB8);

    if (isSelected) {
      return Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: primaryColor,
              shape: BoxShape.circle,
            ),
          ),
          Icon(icon, color: Colors.white),
        ],
      );
    } else {
      return Icon(icon, color: Colors.grey);
    }
  }

  @override
  Widget build(BuildContext context) {
    const Color primaryColor = Color(0xFF005EB8);

    return Scaffold(
      body: _pages[_currentIndex],

      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
        ),
        child: SalomonBottomBar(
          currentIndex: _currentIndex,
          onTap: _onTabTapped,
          itemShape: const CircleBorder(),
          selectedColorOpacity: 0.0,
          selectedItemColor: Colors.transparent,
          unselectedItemColor: Colors.transparent,
          items: [
            SalomonBottomBarItem(
              icon: _buildBubbleIcon(Icons.home, _currentIndex == 0),
              title: Container(height: 0.0),
            ),
            SalomonBottomBarItem(
              icon: _buildBubbleIcon(Icons.camera_alt, _currentIndex == 1),
              title: Container(height: 0.0),
            ),
            SalomonBottomBarItem(
              icon: _buildBubbleIcon(Icons.bar_chart, _currentIndex == 2),
              title: Container(height: 0.0),
            ),
            SalomonBottomBarItem(
              icon: _buildBubbleIcon(Icons.person, _currentIndex == 3),
              title: Container(height: 0.0),
            ),
          ],
        ),
      ),
    );
  }
}