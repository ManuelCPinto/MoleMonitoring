import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:molemonitoringapp/screens/camerascreen.dart';
import 'package:molemonitoringapp/screens/galleryscreen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  Future<void> _navigateToCameraScreen(BuildContext context) async {
    try {
      final cameras = await availableCameras();
      if (cameras.isNotEmpty) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => CameraScreen(camera: cameras.first),
          ),
        );
      } else {
        print('No cameras available');
      }
    } catch (e) {
      print('Error accessing cameras: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mole Monitor'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () {
              Scaffold.of(context).openDrawer(); // Open the menu
            },
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.person), // Profile icon
            onPressed: () {
              // TODO: Add profile screen navigation
            },
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          children: [
            DrawerHeader(
              decoration: BoxDecoration(color: Colors.blue),
              child: Text(
                'Menu',
                style: TextStyle(color: Colors.white, fontSize: 24),
              ),
            ),
            ListTile(
              leading: Icon(Icons.camera_alt),
              title: Text('Take a Picture'),
              onTap: () => _navigateToCameraScreen(context),
            ),
            ListTile(
              leading: Icon(Icons.image),
              title: Text('Select from Gallery'),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const GalleryScreen()),
                );
              },
            ),
          ],
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SizedBox(
              width: 150,
              height: 60,
              child: FloatingActionButton(
                onPressed: () => _navigateToCameraScreen(context),
                child: Text(
                  'Go to this screen that is very cool',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
