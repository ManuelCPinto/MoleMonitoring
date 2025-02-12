import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:molemonitoringapp/screens/camerascreen.dart';
class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {


  @override
  void initState() {
    super.initState();
  }
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
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mole Monitor'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),

      body: Center(

        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SizedBox(
              width: 150, // Adjust width as needed
              height: 60,  // Adjust height as needed
              child: FloatingActionButton(
                onPressed: () => _navigateToCameraScreen(context),
                child: Text(
                  'Go to this screen that is very cool',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center, // Ensures text is centered
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}

