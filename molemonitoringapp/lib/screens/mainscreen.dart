import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '/utils/database_helper.dart';

class HomeScreen extends StatelessWidget {
  final Function(int) onTabTapped; // Callback to change navbar tab
  const HomeScreen({Key? key, required this.onTabTapped}) : super(key: key);

  // Helper method to get the latest prediction from the DB.
  Future<Map<String, dynamic>?> _getLatestPrediction() async {
    final predictions = await DatabaseHelper().getPredictions();
    if (predictions.isNotEmpty) {
      return predictions.first; // Assumes records are ordered DESC.
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    // The Description Section below still uses placeholder text.
    // Only the "Latest Analysis Result" card is updated.
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
                  padding:
                  const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
                  decoration: BoxDecoration(
                    color: const Color(0xFF005EB8),
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

              // Latest Analysis Result Section (updated with DB retrieval)
              // Latest Analysis Result Section (updated with DB retrieval)
              FutureBuilder<Map<String, dynamic>?>(
                future: _getLatestPrediction(), // Helper method to retrieve the latest prediction from the DB.
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Card(
                      color: Colors.white,
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Center(child: CircularProgressIndicator()),
                      ),
                    );
                  }
                  if (!snapshot.hasData || snapshot.data == null) {
                    return Card(
                      color: Colors.white,
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text(
                          "No previous results",
                          style: TextStyle(fontSize: 16, color: Colors.grey),
                        ),
                      ),
                    );
                  }

                  final predictionRecord = snapshot.data!;
                  final String lastPrediction = predictionRecord['prediction'] ?? "";
                  final String confidence = predictionRecord['confidence'] ?? "";
                  final String timestamp = predictionRecord['timestamp'] ?? "";
                  // Optionally, you can also use processing_time if needed.
                  // final String processingTime = predictionRecord['processing_time'] ?? "";

                  // Decode the detailed predictions JSON.
                  Map<String, dynamic> detailedPredictions;
                  try {
                    detailedPredictions =
                    Map<String, dynamic>.from(jsonDecode(predictionRecord['details']));
                  } catch (e) {
                    // Fallback if the JSON is not in the expected format.
                    detailedPredictions = {
                      "akiec": "<0.1%",
                      "bcc": "<0.1%",
                      "bkl": "<0.1%",
                      "df": "<0.1%",
                      "mel": "<0.1%",
                      "nv": "<0.1%",
                      "vasc": "100%"
                    };
                  }

                  final bool isMalignant =
                  ["akiec", "bcc", "mel"].contains(lastPrediction.toLowerCase());

                  return Card(
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
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "Identified as: ${lastPrediction.toUpperCase()}",
                                style: GoogleFonts.lato(
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                  color: isMalignant ? Colors.red : Colors.green,
                                ),
                              ),
                              const SizedBox(height: 5),
                              Text(
                                "Confidence: $confidence",
                                style: GoogleFonts.lato(fontSize: 16, color: Colors.grey),
                              ),
                              const SizedBox(height: 5),
                              Text(
                                "Timestamp: $timestamp",
                                style: GoogleFonts.lato(fontSize: 16, color: Colors.grey),
                              ),
                              const SizedBox(height: 15),
                              SizedBox(
                                height: 200,
                                child: BarChart(
                                  BarChartData(
                                    alignment: BarChartAlignment.spaceAround,
                                    maxY: 100,
                                    barGroups: detailedPredictions.entries.map((entry) {
                                      return BarChartGroupData(
                                        x: detailedPredictions.keys.toList().indexOf(entry.key),
                                        barRods: [
                                          BarChartRodData(
                                            // Remove any '%' symbol and parse to double.
                                            toY: double.tryParse(
                                                entry.value.toString().replaceAll('%', '')) ??
                                                0,
                                            fromY: 0,
                                            color: entry.key.toLowerCase() ==
                                                lastPrediction.toLowerCase()
                                                ? Colors.blue
                                                : Colors.grey,
                                            width: 16,
                                          ),
                                        ],
                                        showingTooltipIndicators: [0],
                                      );
                                    }).toList(),
                                    titlesData: FlTitlesData(
                                      bottomTitles: AxisTitles(
                                        sideTitles: SideTitles(
                                          showTitles: true,
                                          getTitlesWidget: (double value, TitleMeta meta) {
                                            return Text(
                                              detailedPredictions.keys
                                                  .toList()[value.toInt()]
                                                  .toUpperCase(),
                                              style: const TextStyle(fontSize: 10),
                                            );
                                          },
                                          reservedSize: 22,
                                          interval: 1,
                                        ),
                                      ),
                                      leftTitles: AxisTitles(
                                        sideTitles: SideTitles(showTitles: false),
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 20),
                              Text(
                                isMalignant
                                    ? "⚠️ This mole shows characteristics of a malignant type. Please consult a dermatologist as soon as possible."
                                    : "✅ This mole appears benign. However, if you notice changes over time, consult a medical professional.",
                                style: GoogleFonts.lato(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: isMalignant ? Colors.red : Colors.green,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
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
                  child: Text(
                    "This is an AI-generated prediction based on the uploaded mole image. "
                        "If you notice changes or have concerns, please consult a healthcare professional.",
                    style:
                    GoogleFonts.lato(fontSize: 16, color: Colors.black87),
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
