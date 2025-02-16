import 'dart:io';
import 'package:flutter/material.dart';
import 'package:gal/gal.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:http_parser/http_parser.dart';

class DisplayPictureScreen extends StatelessWidget {
  final String imagePath;
  const DisplayPictureScreen({Key? key, required this.imagePath}) : super(key: key);
  final String accessToken = "ya29.a0AXeO80Q8wD1xn6yeNkON3aegckL_q7nzGRFq3-lavTZWWA3Z2aIyuh9GN_nND_0w5S2tqRXNxHSnZN2ARslfbMErWNMzDnHV0LJMNrkP-nvjMFqgAI79lM793r8jiIpSxOzc8Oa9YlXV6ZN3nlywC-buQp0Oe38KWe9u1D_y6CNtSK4aCgYKAakSARMSFQHGX2Mi25oiuEsqP3YP4zys8BeXBg0182";
  final String parseURI = 'https://europe-west3-aiplatform.googleapis.com/v1/projects/sic-molemonitoring/locations/europe-west3/endpoints/4241137405727342592:predict';
  // Function to send a prediction request with an image file

  Future<void> sendPredictionRequest(String imagePath, String accessToken) async {
    // Replace with your actual Vertex AI endpoint URL.
    final uri = Uri.parse(
      parseURI
    );

    // Read the original image file as bytes.
    final originalBytes = await File(imagePath).readAsBytes();

    // Define 1.5 MB in bytes.
    final int sizeThreshold = (1.5 * 1024 * 1024).toInt();

    // If the image is larger than the threshold, compress it.
    List<int>? finalBytes;
    if (originalBytes.length > sizeThreshold) {
      print("Image exceeds 1.5 MB, compressing...");
      final compressedBytes = await FlutterImageCompress.compressWithFile(
        imagePath,
        quality: 50,         // Adjust quality as needed (0-100)
        minWidth: 800,       // Adjust minimum width if needed
        minHeight: 800,      // Adjust minimum height if needed
        format: CompressFormat.jpeg,  // Ensure the output is JPEG
      );
      finalBytes = compressedBytes;
    } else {
      finalBytes = originalBytes;
    }
    //File('my_image.jpg').writeAsBytes(finalBytes!);
    //await Gal.putImage(imagePath);
    // Convert the image bytes to a base64 string.
    final base64Image = base64Encode(finalBytes!);

    // Build the JSON payload with the "instances" field.
    final payload = json.encode({
      "instances": [
        {"image": base64Image}
      ]
    });

    // Send the POST request with the proper headers.
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: payload,
    );

    if (response.statusCode == 200) {
      final result = json.decode(response.body);
      print('Prediction result: $result');
      print(base64Image);
      print(response.body);
    } else {
      print('Error: ${response.statusCode} - ${response.body}');
    }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white), // sets arrow color to fully opaque white
        title: const Text(
          'Picture Preview',
          style: TextStyle(
            color: Colors.white, // Full opacity white
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
      ),
      backgroundColor: Colors.black,
      body: Column(
        children: [
          Expanded(
            child: Image.file(
              File(imagePath),
              fit: BoxFit.contain,
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // "Process" button with elevated styling
                ElevatedButton(
                  onPressed: () {
                    // Placeholder for your future function
                    sendPredictionRequest(imagePath, accessToken);
                    print("Future function implemented here");
                  },
                  child: const Text('Process'),
                ),
                // "Redo" button with outlined styling
                OutlinedButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red, // Change text color
                    side: BorderSide(color: Colors.red), // Optional: Change border color
                  ),
                  child: const Text('Redo'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
