import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class HomeScreen extends StatelessWidget {
  final Function(int) onTabTapped; // Callback to change navbar tab
  const HomeScreen({Key? key, required this.onTabTapped}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bool hasResults = false; // Change this based on actual results
    final String lastPrediction = "Benign"; // Example result
    final String? imageUrl = null; // Replace with actual image if available

    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 30),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              FittedBox(
                fit: BoxFit.scaleDown, // Prevents overflow while keeping it in one line
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
                  decoration: BoxDecoration(
                    color: Color(0xFF005EB8),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    'Mole Monitor',
                    style: GoogleFonts.lato(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Image Placeholder / Redirect to Camera
              GestureDetector(
                onTap: () {
                  onTabTapped(1); // Triggers navbar Camera Tab
                },
                child: Container(
                  width: double.infinity,
                  height: 200,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(color: Colors.grey, width: 2),
                  ),
                  child: imageUrl != null
                      ? ClipRRect(
                    borderRadius: BorderRadius.circular(15),
                    child: Image.network(imageUrl, fit: BoxFit.cover),
                  )
                      : const Center(
                    child: Icon(Icons.add, size: 50, color: Colors.grey),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Last Prediction Result Section
              Card(
                color: Colors.white,
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Latest Analysis Result",
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 10),
                      hasResults
                          ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            lastPrediction,
                            style: GoogleFonts.lato(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: lastPrediction == "Benign" ? Colors.green : Colors.red,
                            ),
                          ),
                          const SizedBox(height: 10),
                          ElevatedButton(
                            onPressed: () {
                              onTabTapped(2); // Triggers navbar Results Tab
                            },
                            child: const Text("View Details"),
                          ),
                        ],
                      )
                          : Text(
                        "No previous results",
                        style: GoogleFonts.lato(fontSize: 16, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Description Section
              Card(
                color: Colors.white,
                elevation: 3,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: hasResults
                      ? Text(
                    "This is an AI-generated prediction based on the uploaded mole image. "
                        "If you notice changes or have concerns, please consult a healthcare professional.",
                    style: GoogleFonts.lato(fontSize: 16, color: Colors.black87),
                  )
                      : Text(
                    "Once you upload an image, your results and explanation will appear here.",
                    style: GoogleFonts.lato(fontSize: 16, color: Colors.grey),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      backgroundColor: Colors.white38,
    );
  }
}
