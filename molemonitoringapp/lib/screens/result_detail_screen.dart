import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '/utils/database_helper.dart';
import '../bottom_nav_screen.dart';

class ResultDetailScreen extends StatelessWidget {
  final Map<String, dynamic> prediction;
  const ResultDetailScreen({Key? key, required this.prediction})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final String lastPrediction = prediction['prediction'] ?? "Unknown";
    final String confidence = prediction['confidence'] ?? "N/A";
    final String timestamp = prediction['timestamp'] ?? "No timestamp";
    final int? recordId = prediction['id'];

    Map<String, dynamic> detailedPredictions;
    try {
      detailedPredictions =
          Map<String, dynamic>.from(jsonDecode(prediction['details']));
    } catch (e) {
      detailedPredictions = {};
    }

    final bool isMalignant =
        ["akiec", "bcc", "mel"].contains(lastPrediction.toLowerCase());

    final double numericConfidence =
        double.tryParse(confidence.replaceAll('%', '')) ?? 0.0;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(
              height: 160,
              child: Stack(
                children: [
                  Positioned.fill(
                    child: CustomPaint(
                      painter: _CurvedHeaderPainter(const Color(0xFF005EB8)),
                    ),
                  ),
                  Positioned(
                    top: 40,
                    left: 16,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  Positioned(
                    top: 40,
                    right: 16,
                    child: IconButton(
                      icon: const Icon(Icons.delete, color: Colors.white),
                      onPressed: () =>
                          _showDeleteConfirmation(context, recordId),
                    ),
                  ),
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 40),
                      child: Text(
                        "Analysis Result",
                        style: GoogleFonts.roboto(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: const [
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
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: Column(
                children: [
                  numericConfidence < 50
                      ? _buildInconclusiveCard(context)
                      : Column(
                          children: [
                            _buildAnalysisCard(
                              lastPrediction: lastPrediction,
                              confidence: confidence,
                              timestamp: timestamp,
                              isMalignant: isMalignant,
                            ),
                            const SizedBox(height: 20),
                            if (detailedPredictions.isNotEmpty)
                              _buildCard(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      "Detailed Chart",
                                      style: GoogleFonts.roboto(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black87,
                                      ),
                                    ),
                                    const SizedBox(height: 16),
                                    SizedBox(
                                      height: 240,
                                      child: _buildVerticalBarChart(
                                        detailedPredictions,
                                        lastPrediction,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                  const SizedBox(height: 20),
                  _buildCard(
                    child: Text(
                      "If you notice changes or have concerns, please consult a healthcare professional.",
                      style: GoogleFonts.roboto(
                          fontSize: 16, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showDeleteConfirmation(BuildContext context, int? recordId) {
    if (recordId == null) return;
    showDialog(
      context: context,
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: const Text("Delete Record"),
          content: const Text(
              "Are you sure you want to permanently delete this result?"),
          actions: [
            TextButton(
              child: const Text("Cancel"),
              onPressed: () => Navigator.pop(ctx),
            ),
            TextButton(
              child: const Text("Delete", style: TextStyle(color: Colors.red)),
              onPressed: () async {
                await DatabaseHelper().deletePredictionById(recordId);
                Navigator.pop(ctx);
                Navigator.pop(context);
              },
            ),
          ],
        );
      },
    );
  }

  Widget _buildInconclusiveCard(BuildContext context) {
    return _buildCard(
      child: Column(
        children: [
          Text(
            "Scan Inconclusive",
            style: GoogleFonts.roboto(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            "This scan did not produce a conclusive result.\n"
            "Please retake your scan for a clearer analysis.",
            style: GoogleFonts.roboto(fontSize: 16, color: Colors.black54),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (ctx) => const BottomNavScreen(
                      initialIndex: 1, showSuccessModal: false),
                ),
              );
            },
            icon: const Icon(Icons.camera_alt),
            label: const Text("Retake Scan"),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF005EB8),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisCard({
    required String lastPrediction,
    required String confidence,
    required String timestamp,
    required bool isMalignant,
  }) {
    return _buildCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Analysis Result",
            style: GoogleFonts.roboto(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 12),
          RichText(
            text: TextSpan(
              style: GoogleFonts.roboto(fontSize: 16, color: Colors.black87),
              children: [
                const TextSpan(
                  text:
                      "Based on the last scan, the lesion presents characteristics of ",
                ),
                TextSpan(
                  text: lastPrediction.toUpperCase(),
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isMalignant ? Colors.red : const Color(0xFF005EB8),
                  ),
                ),
                const TextSpan(text: " with a confidence of "),
                TextSpan(
                  text: confidence,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const TextSpan(text: "."),
              ],
            ),
          ),
          const SizedBox(height: 12),
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
          Text(
            isMalignant
                ? "⚠️ This lesion may be malignant. This result is generated by AI; please consult a dermatologist immediately."
                : "✅ This lesion appears benign. This result is generated by AI; continue to monitor for any changes.",
            style: GoogleFonts.roboto(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isMalignant ? Colors.red : const Color(0xFF005EB8),
            ),
          ),
        ],
      ),
    );
  }

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

  Widget _buildVerticalBarChart(
      Map<String, dynamic> predictions, String lastPred) {
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
                if (value < 0 || value >= entries.length)
                  return const SizedBox();
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

class _CircularGaugePainter extends CustomPainter {
  final double percentage;
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

    final trackPaint = Paint()
      ..color = trackColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (percentage / 100) * 2 * 3.141592653589793;

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

class _CurvedHeaderPainter extends CustomPainter {
  final Color color;
  _CurvedHeaderPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color;
    final path = Path();

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
