import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(

      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 30),

          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              // Hero Section with a Gradient Background
              const SizedBox(height: 20),

              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Colors.deepPurple, Colors.lightBlueAccent], // Midnight Blue gradient
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Column(
                  children: [
                    const Icon(
                      Icons.health_and_safety,
                      size: 80,
                      color: Color(0xFF00BCD4), // Cyan
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'Welcome to Mole Monitor!',
                      style: GoogleFonts.lato(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 5),
                    Text(
                      'Track your skin health and monitor moles effortlessly.',
                      style: GoogleFonts.lato(
                        fontSize: 16,
                        color: Colors.white70,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 30),
              // Latest Analysis Card
              Card(
                color: const Color(0xFF1A1A2E), // Dark background
                elevation: 3,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                child: ListTile(
                  leading: const Icon(Icons.info, color: Color(0xFF00BCD4)), // Cyan
                  title: Text('No recent analysis', style: GoogleFonts.lato(color: Colors.white)),
                  subtitle: Text('Your latest mole analysis will appear here.', style: GoogleFonts.lato(color: Colors.white70)),
                  trailing: IconButton(
                    icon: const Icon(Icons.arrow_forward, color: Color(0xFF00BCD4)), // Cyan
                    onPressed: () {
                      Navigator.pushNamed(context, '/results');
                    },
                  ),
                ),
              ),
              const SizedBox(height: 30),
              // Feature Highlights Section
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Features:',
                    style: GoogleFonts.lato(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black),
                  ),
                  const SizedBox(height: 10),
                  Card(
                    color: const Color(0xFF1A1A2E), // Dark background
                    child: ListTile(
                      leading: const Icon(Icons.camera_alt, color: Color(0xFF00BCD4)), // Cyan
                      title: Text('Capture High-Quality Photos', style: GoogleFonts.lato(color: Colors.white)),
                      subtitle: Text('Use your camera to document skin changes.', style: GoogleFonts.lato(color: Colors.white70)),
                    ),
                  ),
                  Card(
                    color: const Color(0xFF1A1A2E),
                    child: ListTile(
                      leading: const Icon(Icons.history, color: Color(0xFF00BCD4)),
                      title: Text('Review Past Results', style: GoogleFonts.lato(color: Colors.white)),
                      subtitle: Text('Easily access your previous analyses.', style: GoogleFonts.lato(color: Colors.white70)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 30),
              // Tips Section
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Tips for Skin Monitoring:',
                    style: GoogleFonts.lato(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black),
                  ),
                  const SizedBox(height: 10),
                  Card(
                    color: const Color(0xFF1A1A2E),
                    child: ListTile(
                      leading: const Icon(Icons.check_circle, color: Color(0xFF00E5FF)), // Light Cyan
                      title: Text('Take photos in good lighting conditions.', style: GoogleFonts.lato(color: Colors.white)),
                    ),
                  ),
                  Card(
                    color: const Color(0xFF1A1A2E),
                    child: ListTile(
                      leading: const Icon(Icons.check_circle, color: Color(0xFF00E5FF)),
                      title: Text('Use the same angle for better comparison.', style: GoogleFonts.lato(color: Colors.white)),
                    ),
                  ),
                  Card(
                    color: const Color(0xFF1A1A2E),
                    child: ListTile(
                      leading: const Icon(Icons.check_circle, color: Color(0xFF00E5FF)),
                      title: Text('Consult a dermatologist for any concerns.', style: GoogleFonts.lato(color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      backgroundColor: Colors.white38, // Deep dark background
    );
  }
}
