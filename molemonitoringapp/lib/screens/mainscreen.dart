import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Example last prediction data (replace with actual data logic)
    final bool hasResults = false; // Change this based on actual results
    final String lastPrediction = "Benign"; // Example result

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

              // Last Prediction Result Section
              Card(
                color: Colors.white, // Light background for contrast
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Text(
                        "Latest Analysis Result",
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 10),
                      hasResults
                          ? Column(
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
                              Navigator.pushNamed(context, '/results');
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
              const SizedBox(height: 30),

              // Navigation Cards Section
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Quick Actions:',
                    style: GoogleFonts.lato(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black),
                  ),
                  const SizedBox(height: 10),

                  _buildNavigationCard(
                    context,
                    icon: Icons.camera_alt,
                    title: "Monitor Now",
                    subtitle: "Capture a new mole image for analysis",
                    onTap: () {
                      Navigator.pushNamed(context, '/camera');
                    },
                  ),
                  _buildNavigationCard(
                    context,
                    icon: Icons.history,
                    title: "Check Previous Results",
                    subtitle: "View all your past skin analysis",
                    onTap: () {
                      Navigator.pushNamed(context, '/results');
                    },
                  ),
                  _buildNavigationCard(
                    context,
                    icon: Icons.person,
                    title: "View Profile",
                    subtitle: "Edit your profile and settings",
                    onTap: () {
                      Navigator.pushNamed(context, '/profile');
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      backgroundColor: Colors.white38,
    );
  }

  // Custom method to generate navigation cards
  Widget _buildNavigationCard(BuildContext context, {required IconData icon, required String title, required String subtitle, required VoidCallback onTap}) {
    return Card(
      color: const Color(0xFF1A1A2E), // Dark background
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF00BCD4)), // Cyan
        title: Text(title, style: GoogleFonts.lato(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle, style: GoogleFonts.lato(color: Colors.white70)),
        trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white70),
        onTap: onTap,
      ),
    );
  }
}
