import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '/screens/camera.dart';

class CameraTab extends StatefulWidget {
  const CameraTab({Key? key}) : super(key: key);

  @override
  State<CameraTab> createState() => _CameraTabState();
}

class _CameraTabState extends State<CameraTab> {
  late Future<List<CameraDescription>> _camerasFuture;

  @override
  void initState() {
    super.initState();
    _camerasFuture = availableCameras();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<CameraDescription>>(
      future: _camerasFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            appBar: AppBar(title: const Text('Camera')),
            body: const Center(child: CircularProgressIndicator()),
          );
        } else if (snapshot.hasError) {
          return Scaffold(
            appBar: AppBar(title: const Text('Camera')),
            body: Center(
              child: Text('Error: ${snapshot.error}', style: GoogleFonts.lato()),
            ),
          );
        } else if (snapshot.hasData && snapshot.data!.isNotEmpty) {
          return CameraApp(camera: snapshot.data![0]); // ✅ Directly show camera
        } else {
          return Scaffold(
            appBar: AppBar(title: const Text('Camera')),
            body: Center(
              child: Text('No cameras available', style: GoogleFonts.lato()),
            ),
          );
        }
      },
    );
  }
}
