import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  static const Color accentBlue = Color(0xFF005EB8);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      // Use SingleChildScrollView in case content expands
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Curved header at the top (height = 160, same as main page)
            SizedBox(
              height: 160,
              child: Stack(
                children: [
                  Positioned.fill(
                    child: CustomPaint(
                      painter: _CurvedHeaderPainter(accentBlue),
                    ),
                  ),
                  // Title "Profile" in the center
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 50),
                      child: Text(
                        "Profile",
                        style: GoogleFonts.roboto(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            const Shadow(
                              color: Colors.black26,
                              blurRadius: 4,
                              offset: Offset(0, 2),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Stack to overlap the avatar on the header
            Stack(
              alignment: Alignment.topCenter,
              children: [
                // Card with user details (less margin on top to reduce total height)
                Container(
                  margin: const EdgeInsets.only(top: 40),
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                  child: _buildCard(
                    child: Column(
                      children: [
                        const SizedBox(height: 50), // Reserve space for avatar overlap
                        Text(
                          'User Test',
                          style: GoogleFonts.roboto(fontSize: 22, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'user@example.com',
                          style: GoogleFonts.roboto(fontSize: 14, color: Colors.grey),
                        ),
                        const SizedBox(height: 16),

                        // Location / fun detail row
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.location_on, color: Colors.redAccent, size: 18),
                            const SizedBox(width: 4),
                            Text(
                              "Lisboa, Portugal",
                              style: GoogleFonts.roboto(fontSize: 14, color: Colors.grey[700]),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),

                        // Edit Profile Button
                        ElevatedButton.icon(
                          onPressed: () {
                            // TODO: Implement edit profile functionality
                          },
                          icon: const Icon(Icons.edit),
                          label: const Text("Edit Profile"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: accentBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                            textStyle: GoogleFonts.roboto(fontWeight: FontWeight.w600),
                          ),
                        ),
                        const SizedBox(height: 20),

                        // Logout Button
                        OutlinedButton.icon(
                          onPressed: () {
                            // TODO: Implement logout functionality
                          },
                          icon: const Icon(Icons.logout, color: Colors.red),
                          label: const Text(
                            "Logout",
                            style: TextStyle(color: Colors.red),
                          ),
                          style: OutlinedButton.styleFrom(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            side: const BorderSide(color: Colors.red),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                            textStyle: GoogleFonts.roboto(fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Circle avatar overlapping the card and header
                Positioned(
                  top: 0,
                  child: CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.grey[300],
                    child: const Icon(
                      Icons.person,
                      size: 50,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// A simple card widget with a light shadow
  Widget _buildCard({required Widget child}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}

/// Same curved header painter as in your main page
class _CurvedHeaderPainter extends CustomPainter {
  final Color color;
  _CurvedHeaderPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color;
    final path = Path();

    // Draw a rectangle with a curved bottom edge
    path.moveTo(0, 0);
    path.lineTo(0, size.height - 50);
    path.quadraticBezierTo(
      size.width * 0.5,
      size.height,
      size.width,
      size.height - 50,
    );
    path.lineTo(size.width, 0);
    path.close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_CurvedHeaderPainter oldDelegate) => false;
}
