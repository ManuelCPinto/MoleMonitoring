import 'dart:convert';
import 'dart:ui'; // For ImageFilter
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '/utils/database_helper.dart';

class HomeScreen extends StatefulWidget {
  final Function(int) onTabTapped;
  const HomeScreen({Key? key, required this.onTabTapped}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const Color accentBlue = Color(0xFF005EB8);

  late Future<Map<String, dynamic>?> _predictionFuture;
  bool _showInfo = false;

  @override
  void initState() {
    super.initState();
    _predictionFuture = _getLatestPrediction();
  }

  Future<Map<String, dynamic>?> _getLatestPrediction() async {
    final predictions = await DatabaseHelper().getPredictions();
    if (predictions.isNotEmpty) {
      return predictions.first;
    }
    return null;
  }

  /// Interprets a raw confidence percentage (e.g., "85%") into a descriptive phrase.
  String interpretConfidence(String confidenceStr) {
    final numeric = double.tryParse(confidenceStr.replaceAll('%', '')) ?? 0.0;
    if (numeric < 50) {
      return "Inconclusive";
    } else if (numeric < 80) {
      return "Likely";
    } else if (numeric < 90) {
      return "Very Likely";
    } else if (numeric < 100) {
      return "Most Likely";
    } else {
      return "Almost Certain";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      // Header remains unchanged.
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Curved header (unchanged)
            SizedBox(
              height: 160,
              child: Stack(
                children: [
                  Positioned.fill(
                    child: CustomPaint(
                      painter: _CurvedHeaderPainter(accentBlue),
                    ),
                  ),
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 40),
                      child: Text(
                        "Homepage",
                        style: GoogleFonts.roboto(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            Shadow(
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

            // Main content
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: FutureBuilder<Map<String, dynamic>?>(
                future: _predictionFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return _buildCard(
                      child: const Center(child: CircularProgressIndicator()),
                    );
                  }
                  if (!snapshot.hasData || snapshot.data == null) {
                    return _buildCard(
                      child: Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.camera_alt,
                              size: 50,
                              color: accentBlue,
                            ),
                            const SizedBox(height: 10),
                            Text(
                              "No scans found",
                              style: GoogleFonts.roboto(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                            const SizedBox(height: 5),
                            Text(
                              "Tap the camera to scan your lesion and start monitoring!",
                              style: GoogleFonts.roboto(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    );
                  }

                  final data = snapshot.data!;
                  final String lastPrediction = data['prediction'] ?? "";
                  final String confidence = data['confidence'] ?? "";
                  final String timestamp = data['timestamp'] ?? "";

                  Map<String, dynamic> details;
                  try {
                    details = Map<String, dynamic>.from(jsonDecode(data['details']));
                  } catch (e) {
                    details = {
                      "akiec": "<0.1%",
                      "bcc": "<0.1%",
                      "bkl": "<0.1%",
                      "df": "<0.1%",
                      "mel": "<0.1%",
                      "nv": "<0.1%",
                      "vasc": "100%"
                    };
                  }

                  // Determine if the lesion is malignant
                  final bool isMalignant = ["akiec", "bcc", "mel"]
                      .contains(lastPrediction.toLowerCase());

                  return Column(
                    children: [
                      // Latest Analysis Card with gauge in top-right
                      _buildLatestAnalysisCard(lastPrediction, confidence, timestamp, isMalignant),
                      const SizedBox(height: 20),
                      // Analysis Chart Card (unchanged)
                      _buildCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "Analysis Chart",
                              style: GoogleFonts.roboto(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                            const SizedBox(height: 16),
                            SizedBox(
                              height: 240,
                              child: _buildVerticalBarChart(details, lastPrediction),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Latest Analysis Card with gauge in the top-right. The portion below
  /// the timestamp can extend to the card's full width.
  Widget _buildLatestAnalysisCard(String lastPrediction, String confidenceStr, String timestamp, bool isMalignant) {
    final double numericConfidence = double.tryParse(confidenceStr.replaceAll('%', '')) ?? 0.0;
    final String confidencePhrase = interpretConfidence(confidenceStr);
    final Color typeColor = isMalignant ? Colors.red : accentBlue;

    return _buildCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stack for top lines: Title + Narrative + Gauge in top-right
          Stack(
            children: [
              // Title + narrative portion (with right padding for gauge)
              Padding(
                padding: const EdgeInsets.only(right: 100),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Latest Analysis",
                      style: GoogleFonts.roboto(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Narrative text
                    RichText(
                      text: TextSpan(
                        style: GoogleFonts.roboto(fontSize: 16, color: Colors.black87),
                        children: [
                          const TextSpan(text: "Based on the last scan, the lesion presents characteristics of "),
                          TextSpan(
                            text: lastPrediction.toUpperCase(),
                            style: TextStyle(fontWeight: FontWeight.bold, color: typeColor),
                          ),
                          const TextSpan(text: " with a confidence of "),
                          TextSpan(
                            text: "${numericConfidence.toStringAsFixed(1)}%",
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const TextSpan(text: " ("),
                          TextSpan(
                            text: confidencePhrase,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const TextSpan(text: ")."),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              // Circular gauge in top-right
              Positioned(
                top: 0,
                right: 0,
                child: SizedBox(
                  width: 80,
                  height: 80,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      CustomPaint(
                        size: const Size(80, 80),
                        painter: _CircularGaugePainter(
                          percentage: numericConfidence,
                          trackColor: Colors.grey[300]!,
                          fillColor: accentBlue,
                        ),
                      ),
                      Text(
                        "${numericConfidence.toStringAsFixed(1)}%",
                        style: GoogleFonts.roboto(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Everything below the stack uses full width
          // Timestamp row
          Row(
            children: [
              Icon(Icons.access_time, size: 18, color: Colors.grey[700]),
              const SizedBox(width: 6),
              Text(
                timestamp,
                style: GoogleFonts.roboto(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Advisory message
          Text(
            isMalignant
                ? "⚠️ This lesion may be malignant. This result is generated by AI; please consult a dermatologist immediately."
                : "✅ This lesion appears benign. This result is generated by AI; continue to monitor for any changes.",
            style: GoogleFonts.roboto(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isMalignant ? Colors.red : accentBlue,
            ),
          ),
          const SizedBox(height: 16),

          // Show More Info button
          _buildButton(
            text: _showInfo ? "Hide Info" : "Show More Info",
            onTap: () {
              setState(() {
                _showInfo = !_showInfo;
              });
            },
            backgroundColor: accentBlue,
            textColor: Colors.white,
          ),
          AnimatedSize(
            duration: const Duration(milliseconds: 400),
            curve: Curves.easeInOut,
            child: _showInfo
                ? Padding(
              padding: const EdgeInsets.only(top: 8.0),
              child: Text(
                _mockInfoText(lastPrediction),
                style: GoogleFonts.roboto(fontSize: 14, color: Colors.black87),
              ),
            )
                : const SizedBox(),
          ),
        ],
      ),
    );
  }

  /// Simple card widget with a light shadow.
  Widget _buildCard({required Widget child}) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: child,
    );
  }

  /// Custom button style.
  Widget _buildButton({
    required String text,
    required VoidCallback onTap,
    required Color backgroundColor,
    required Color textColor,
  }) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        textStyle: GoogleFonts.roboto(fontSize: 14, fontWeight: FontWeight.w600),
        elevation: 2,
      ),
      onPressed: onTap,
      child: Text(text, style: TextStyle(color: textColor)),
    );
  }

  /// Mock info text based on the prediction type.
  String _mockInfoText(String pred) {
    switch (pred.toLowerCase()) {

      case 'akiec':
        return """
AKIEC (Actinic Keratoses / Intraepithelial Carcinoma) are rough, scaly patches caused by prolonged UV exposure. 
They can potentially progress to squamous cell carcinoma if left untreated. 
Early diagnosis and treatment—often via topical therapies, cryotherapy, or minor surgical procedures—can prevent further complications.
Always consult a dermatologist for accurate assessment and management.
""";

      case 'bcc':
        return """
BCC (Basal Cell Carcinoma) is a common form of skin cancer that typically appears as a pearly or waxy bump, 
sometimes with visible blood vessels. It often arises in sun-exposed areas (face, ears, scalp). 
Though it usually grows slowly, early treatment (surgical excision, topical therapies, or radiation) is essential to avoid local tissue damage.
Consult a dermatologist if you notice persistent, non-healing lesions.
""";

      case 'bkl':
        return """
BKL (Benign Keratosis, including seborrheic keratoses, solar lentigo, or lichen-planus-like keratosis) are non-cancerous growths. 
They often have a “stuck-on” appearance, varying in color from light brown to black. 
While generally harmless, changes in size, color, or texture should be evaluated by a dermatologist to rule out malignancy.
""";

      case 'df':
        return """
DF (Dermatofibroma) is a benign, firm nodule often found on the legs or arms. 
They can appear pink, red, or brown, and might dimple inward when pinched. 
Dermatofibromas usually do not require treatment unless they become symptomatic or cause cosmetic concerns.
Any rapid changes or ulcerations should prompt medical evaluation.
""";

      case 'mel':
        return """
MEL (Melanoma) is a serious form of skin cancer originating in melanocytes (pigment-producing cells). 
It may appear as a dark, irregularly shaped mole or a rapidly changing lesion. 
Early detection is crucial—treatment often involves surgical removal and may include additional therapies if it has spread. 
Watch for the ABCDEs (Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolving) and consult a dermatologist immediately if suspicious changes occur.
""";

      case 'nv':
        return """
NV (Melanocytic Nevus or “mole”) refers to a benign proliferation of melanocytes. 
Most moles are harmless, but it’s important to monitor them for any changes in size, shape, or color. 
If a mole exhibits rapid growth, irregular borders, or multiple colors, seek a dermatologist’s evaluation to rule out malignant transformation.
""";

      case 'vasc':
        return """
VASC (Vascular Lesion) encompasses hemangiomas, angiomas, and other blood vessel–related growths. 
They can vary in color from red to purple and are usually benign. 
While most vascular lesions are harmless, some may bleed or grow in size, warranting medical assessment. 
Always consult a healthcare professional if you notice rapid changes or symptomatic lesions.
""";

      default:
        return """
Monitor any mole or skin lesion for changes in size, shape, or color. 
If you observe rapid evolution or have concerns, consult a qualified dermatologist for an accurate diagnosis and management plan.
""";
    }
  }



  /// Vertical bar chart using fl_chart (unchanged).
  Widget _buildVerticalBarChart(Map<String, dynamic> predictions, String lastPred) {
    final entries = predictions.entries.toList();
    final barGroups = <BarChartGroupData>[];

    for (int i = 0; i < entries.length; i++) {
      final entry = entries[i];
      final rawValue = entry.value.toString().replaceAll('%', '');
      double barValue = double.tryParse(rawValue) ?? 0.0;
      if (barValue < 0.1) barValue = 0.1;
      final bool isActive = entry.key.toLowerCase() == lastPred.toLowerCase();
      final gradient = isActive
          ? const LinearGradient(
        colors: [Colors.blue, Colors.lightBlueAccent],
        begin: Alignment.bottomCenter,
        end: Alignment.topCenter,
      )
          : const LinearGradient(
        colors: [Colors.grey, Colors.grey],
        begin: Alignment.bottomCenter,
        end: Alignment.topCenter,
      );
      barGroups.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: barValue,
              width: 20,
              borderRadius: BorderRadius.circular(6),
              gradient: gradient,
            ),
          ],
          showingTooltipIndicators: [0],
        ),
      );
    }

    return BarChart(
      BarChartData(
        maxY: 120,
        minY: 0,
        groupsSpace: 20,
        barGroups: barGroups,
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 36,
              getTitlesWidget: (double value, TitleMeta meta) {
                if (value < 0 || value >= entries.length) return const SizedBox();
                final String label = entries[value.toInt()].key.toUpperCase();
                return Padding(
                  padding: const EdgeInsets.only(top: 6.0),
                  child: Text(
                    label,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        gridData: FlGridData(show: false),
        borderData: FlBorderData(
          show: true,
          border: const Border(
            left: BorderSide(color: Colors.black54, width: 2),
            bottom: BorderSide(color: Colors.black54, width: 2),
            top: BorderSide.none,
            right: BorderSide.none,
          ),
        ),
        barTouchData: BarTouchData(
          enabled: false,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: Colors.white.withOpacity(0.9),
            fitInsideVertically: true,
            fitInsideHorizontally: true,
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              final String valueStr = entries[groupIndex].value.toString();
              return BarTooltipItem(
                valueStr,
                const TextStyle(
                  color: Colors.black,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              );
            },
          ),
        ),
      ),
      swapAnimationDuration: const Duration(milliseconds: 800),
      swapAnimationCurve: Curves.easeOutQuad,
    );
  }
}

/// A custom painter for drawing a circular (radial) gauge.
class _CircularGaugePainter extends CustomPainter {
  final double percentage; // e.g., 85.0 means 85%
  final Color trackColor;
  final Color fillColor;

  _CircularGaugePainter({
    required this.percentage,
    required this.trackColor,
    required this.fillColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    const strokeWidth = 10.0;
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Draw the track (background circle).
    final trackPaint = Paint()
      ..color = trackColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);

    // Draw the arc for the fill.
    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    // The angle for the arc is based on the percentage.
    // 100% = 360 degrees (in radians = 2 * pi).
    final sweepAngle = (percentage / 100) * 2 * 3.141592653589793;

    // Start angle is -90 degrees so arc starts from the top center.
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -3.141592653589793 / 2,
      sweepAngle,
      false,
      fillPaint,
    );
  }

  @override
  bool shouldRepaint(_CircularGaugePainter oldDelegate) {
    return oldDelegate.percentage != percentage ||
        oldDelegate.trackColor != trackColor ||
        oldDelegate.fillColor != fillColor;
  }
}

/// Custom painter for the curved header (unchanged).
class _CurvedHeaderPainter extends CustomPainter {
  final Color color;
  _CurvedHeaderPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color;
    final path = Path();

    // Draw a rectangle with a curved bottom edge.
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
