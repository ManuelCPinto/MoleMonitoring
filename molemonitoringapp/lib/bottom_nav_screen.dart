import 'package:flutter/material.dart';
import 'package:salomon_bottom_bar/salomon_bottom_bar.dart';
import 'package:molemonitoringapp/screens/camera_tab.dart';
import 'package:molemonitoringapp/screens/mainscreen.dart';
import 'package:molemonitoringapp/screens/resultsscreen.dart';
import 'package:molemonitoringapp/screens/profilescreen.dart';
import 'package:molemonitoringapp/utils/success_modal.dart'; // Your success modal function

class BottomNavScreen extends StatefulWidget {
  final int initialIndex;
  final bool showSuccessModal;
  const BottomNavScreen({
    Key? key,
    this.initialIndex = 0,
    this.showSuccessModal = false,
  }) : super(key: key);

  @override
  State<BottomNavScreen> createState() => _BottomNavScreenState();
}

class _BottomNavScreenState extends State<BottomNavScreen> {
  late int _currentIndex;
  final List<Widget> _pages = [];
  bool _modalFinished = false;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _pages.addAll([
      HomeScreen(onTabTapped: _onTabTapped),
      const CameraTab(),
      const ResultsScreen(),
      const ProfileScreen(),
    ]);
    // If the flag is true, show the success modal and wait for it to close.
    if (widget.showSuccessModal) {
      WidgetsBinding.instance.addPostFrameCallback((_) async {
        await showSuccessModal(context);
        // When modal is dismissed, mark as finished and rebuild.
        setState(() {
          _modalFinished = true;
        });
      });
    } else {
      _modalFinished = true;
    }
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
            decoration: const BoxDecoration(
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
    // Until the modal has finished, show a loading indicator.
    if (!_modalFinished) {
      return Scaffold(
        backgroundColor: Colors.white,
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 8,
              offset: Offset(0, -2),
            ),
          ],
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
