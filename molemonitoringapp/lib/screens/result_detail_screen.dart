import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';

class ResultDetailScreen extends StatelessWidget {
  final Map<String, dynamic> prediction;

  const ResultDetailScreen({Key? key, required this.prediction}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final String lastPrediction = prediction['prediction'] ?? "Unknown";
    final String confidence = prediction['confidence'] ?? "N/A";
    final String timestamp = prediction['timestamp'] ?? "No timestamp";

    // Decode the detailed predictions JSON safely
    Map<String, dynamic> detailedPredictions;
    try {
      detailedPredictions = jsonDecode(prediction['details']);
    } catch (e) {
      detailedPredictions = {};
    }

    final bool isMalignant = ["akiec", "bcc", "mel"].contains(lastPrediction.toLowerCase());

    return Scaffold(
      appBar: AppBar(
        title: const Text("Analysis Result"),
        backgroundColor: Colors.white, // Keep theme consistent
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () {
            Navigator.pop(context); // Go back to ResultsScreen
          },
        ),
      ),
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Analysis Result",
              style: GoogleFonts.lato(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black),
            ),
            const SizedBox(height: 10),
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
              style: GoogleFonts.lato(fontSize: 16, color: Colors.grey[700]),
            ),
            const SizedBox(height: 5),
            Text(
              "Timestamp: $timestamp",
              style: GoogleFonts.lato(fontSize: 14, color: Colors.grey[500]),
            ),
            const SizedBox(height: 20),
            if (detailedPredictions.isNotEmpty)
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
                            toY: double.tryParse(entry.value.toString().replaceAll('%', '')) ?? 0,
                            fromY: 0,
                            color: entry.key.toLowerCase() == lastPrediction.toLowerCase()
                                ? Colors.blue
                                : Colors.grey,
                            width: 16,
                          ),
                        ],
                      );
                    }).toList(),
                    titlesData: FlTitlesData(
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          getTitlesWidget: (double value, TitleMeta meta) {
                            return Text(
                              detailedPredictions.keys.toList()[value.toInt()].toUpperCase(),
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
                  ? "⚠️ This mole shows characteristics of a malignant type. Please consult a dermatologist."
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
      ),
    );
  }
}
