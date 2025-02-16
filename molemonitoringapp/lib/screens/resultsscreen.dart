import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:sqflite/sqflite.dart';
import '/utils/database_helper.dart'; // Ensure you import your DatabaseHelper file
import '/utils/storage_helper.dart';  // Import StorageHelper if you later need to load images

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
        title: const Text('Past Results'),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
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
                    return Card(
                      margin: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      child: ListTile(
                        leading: const Icon(Icons.assignment_outlined),
                        title: Text(
                          prediction['prediction'] ?? 'No prediction',
                          style: GoogleFonts.lato(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: 4.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Confidence: ${prediction['confidence'] ?? 'N/A'}',
                                style: GoogleFonts.lato(),
                              ),
                              Text(
                                'Timestamp: ${prediction['timestamp'] ?? 'N/A'}',
                                style: GoogleFonts.lato(fontSize: 12),
                              ),
                              Text(
                                'Processing Time: ${prediction['processing_time'] ?? 'N/A'}',
                                style: GoogleFonts.lato(fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        // If you decide to store an image path along with the prediction,
                        // you could show a thumbnail here using StorageHelper.
                        // For example:
                        // leading: Image.file(File(prediction['image_path'])),
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
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.history,
                size: 80, color: Colors.deepPurpleAccent),
            const SizedBox(height: 20),
            Text(
              'No results available',
              style: GoogleFonts.lato(
                  fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Text(
              'Your past analysis results will appear here.',
              textAlign: TextAlign.center,
              style: GoogleFonts.lato(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
