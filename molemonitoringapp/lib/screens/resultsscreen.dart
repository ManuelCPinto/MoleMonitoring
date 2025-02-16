import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:sqflite/sqflite.dart';
import '/utils/database_helper.dart';
import 'result_detail_screen.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({Key? key}) : super(key: key);

  @override
  _ResultsScreenState createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  late Future<List<Map<String, dynamic>>> _predictionsFuture;

  @override
  void initState() {
    super.initState();
    _loadPredictions();
  }

  void _loadPredictions() {
    _predictionsFuture = DatabaseHelper().getPredictions();
  }

  Future<void> _refreshPredictions() async {
    setState(() {
      _loadPredictions();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Past Results', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white38,
        elevation: 0,
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.black),
            onPressed: _refreshPredictions,
          ),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _predictionsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (snapshot.hasData) {
            final predictions = snapshot.data!;
            if (predictions.isEmpty) {
              return _buildEmptyState();
            } else {
              return RefreshIndicator(
                onRefresh: _refreshPredictions,
                child: ListView.builder(
                  itemCount: predictions.length,
                  itemBuilder: (context, index) {
                    final prediction = predictions[index];
                    final String timestamp = prediction['timestamp'] ?? 'No date';

                    return Card(
                      color: Colors.white,
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      elevation: 2,
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(12),
                        leading: const Icon(Icons.assignment_outlined, color: Colors.deepPurple),
                        title: Text(
                          prediction['prediction'] ?? 'No prediction',
                          style: GoogleFonts.lato(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        subtitle: Text(
                          'Confidence: ${prediction['confidence'] ?? 'N/A'}\nTimestamp: $timestamp',
                          style: GoogleFonts.lato(fontSize: 14, color: Colors.grey[700]),
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                        onTap: () {
                          Navigator.push(
                            context,
                            PageRouteBuilder(
                              pageBuilder: (context, animation, secondaryAnimation) =>
                                  ResultDetailScreen(prediction: prediction),
                              transitionsBuilder: (context, animation, secondaryAnimation, child) {
                                return FadeTransition(opacity: animation, child: child);
                              },
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
              );
            }
          } else {
            return _buildEmptyState();
          }
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Text('No results available', style: GoogleFonts.lato(fontSize: 18, fontWeight: FontWeight.bold)),
    );
  }
}
