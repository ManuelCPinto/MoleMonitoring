import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:molemonitoringapp/screens/display_picture.dart';
import 'package:molemonitoringapp/utils/storage_helper.dart'; // Import storage helper

class CameraApp extends StatefulWidget {
  final CameraDescription camera;
  const CameraApp({Key? key, required this.camera}) : super(key: key);

  @override
  State<CameraApp> createState() => _CameraAppState();
}

class _CameraAppState extends State<CameraApp> {
  late CameraController controller;
  late Future<void> _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    controller = CameraController(
      widget.camera,
      ResolutionPreset.max,
      enableAudio: false, // 🔥 Fix: Disables microphone permission
    );
    _initializeControllerFuture = controller.initialize();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!controller.value.isInitialized) {
      return const Center(child: CircularProgressIndicator());
    }
    return Scaffold(
      body: CameraPreview(controller),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          try {
            // Ensure the camera is initialized.
            await _initializeControllerFuture;

            // Take a picture
            final image = await controller.takePicture();

            // Save image locally
            final savedImagePath = await StorageHelper.saveImage(File(image.path));

            if (!context.mounted) return;

            // Navigate to display picture screen
            await Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => DisplayPictureScreen(imagePath: savedImagePath),
              ),
            );
          } catch (e) {
            print("Camera error: $e");
          }
        },
        child: const Icon(Icons.camera_alt),
      ),
    );
  }
}
