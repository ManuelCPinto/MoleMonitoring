import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '/utils/database_helper.dart';
import 'result_detail_screen.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({Key? key}) : super(key: key);

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  static const Color accentBlue = Color(0xFF005EB8);
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

  /// Show a confirmation dialog before deletion.
  Future<bool?> _confirmDeletion(BuildContext context, int recordId) async {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: const Text("Delete Record"),
          content: const Text("Are you sure you want to permanently delete this result?"),
          actions: [
            TextButton(
              child: const Text("Cancel"),
              onPressed: () => Navigator.of(ctx).pop(false),
            ),
            TextButton(
              child: const Text("Delete", style: TextStyle(color: Colors.red)),
              onPressed: () async {
                await DatabaseHelper().deletePredictionById(recordId);
                Navigator.of(ctx).pop(true);
              },
            ),
          ],
        );
      },
    );
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
                          ],
                        ),
                      ),
                    ),
                  ),
                  // Optional refresh icon in top-right
                  Positioned(
                    top: 40,
                    right: 20,
                    child: GestureDetector(
                      onTap: _refreshPredictions,
                      child: const Icon(
                        Icons.refresh,
                        color: Colors.white,
                        size: 26,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Main content area
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: FutureBuilder<List<Map<String, dynamic>>>(
                future: _predictionsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return _buildCard(
                      child: const Center(child: CircularProgressIndicator()),
                    );
                  } else if (snapshot.hasError) {
                    return _buildCard(
                      child: Text(
                        'Error: ${snapshot.error}',
                        style: GoogleFonts.roboto(fontSize: 16, color: Colors.red),
                      ),
                    );
                  } else if (snapshot.hasData) {
                    final predictions = snapshot.data!;
                    if (predictions.isEmpty) {
                      return _buildEmptyState();
                    } else {
                      return RefreshIndicator(
                        onRefresh: _refreshPredictions,
                        child: ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: predictions.length,
                          itemBuilder: (context, index) {
                            final prediction = predictions[index];
                            final int recordId = prediction['id'];
                            final String timestamp = prediction['timestamp'] ?? 'No date';
                            return SwipeToDelete(
                              onDelete: () async {
                                await DatabaseHelper().deletePredictionById(recordId);
                                _refreshPredictions();
                              },
                              child: _buildCard(
                                child: ListTile(
                                  contentPadding: const EdgeInsets.all(12),
                                  leading: const Icon(Icons.assignment_outlined, color: Color(0xFF005EB8)),
                                  title: Text(
                                    prediction['prediction'] ?? 'No prediction',
                                    style: GoogleFonts.roboto(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                      color: Colors.black87,
                                    ),
                                  ),
                                  subtitle: Text(
                                    'Confidence: ${prediction['confidence'] ?? 'N/A'}\nTimestamp: $timestamp',
                                    style: GoogleFonts.roboto(fontSize: 14, color: Colors.grey[700]),
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
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return _buildCard(
      child: Center(
        child: Text(
          'No results available',
          style: GoogleFonts.roboto(fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  // Simple card widget with consistent styling.
  Widget _buildCard({required Widget child}) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
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
}

/// Custom widget for swipe-to-delete with limited drag.
class SwipeToDelete extends StatefulWidget {
  final Widget child;
  final Future<void> Function() onDelete;
  const SwipeToDelete({Key? key, required this.child, required this.onDelete}) : super(key: key);

  @override
  _SwipeToDeleteState createState() => _SwipeToDeleteState();
}

class _SwipeToDeleteState extends State<SwipeToDelete> with SingleTickerProviderStateMixin {
  double _dragOffset = 0.0;
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState(){
    super.initState();
    _animationController = AnimationController(vsync: this, duration: const Duration(milliseconds: 200));
    _animation = Tween<double>(begin: _dragOffset, end: 0).animate(_animationController)
      ..addListener(() {
        setState(() {
          _dragOffset = _animation.value;
        });
      });
  }

  @override
  void dispose(){
    _animationController.dispose();
    super.dispose();
  }

  void _animateBack() {
    _animation = Tween<double>(begin: _dragOffset, end: 0).animate(_animationController);
    _animationController.forward(from: 0);
  }

  @override
  Widget build(BuildContext context){
    return LayoutBuilder(
        builder: (context, constraints) {
          double maxDrag = constraints.maxWidth * 0.15;
          return GestureDetector(
            onHorizontalDragUpdate: (details){
              setState(() {
                _dragOffset += details.delta.dx;
                // Clamp dragOffset between 0 and maxDrag
                if (_dragOffset < 0) _dragOffset = 0;
                if (_dragOffset > maxDrag) _dragOffset = maxDrag;
              });
            },
            onHorizontalDragEnd: (details) async {
              if (_dragOffset >= maxDrag) {
                // Show confirmation dialog
                bool? confirmed = await showDialog<bool>(
                  context: context,
                  builder: (context) {
                    return AlertDialog(
                      title: const Text("Delete Record"),
                      content: const Text("Are you sure you want to permanently delete this result?"),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context, false),
                          child: const Text("Cancel"),
                        ),
                        TextButton(
                          onPressed: () async {
                            Navigator.pop(context, true);
                          },
                          child: const Text("Delete", style: TextStyle(color: Colors.red)),
                        ),
                      ],
                    );
                  },
                );
                if (confirmed == true) {
                  await widget.onDelete();
                } else {
                  _animateBack();
                }
              } else {
                _animateBack();
              }
            },
            child: Stack(
              children: [
                // The red square icon remains fixed in position while dragging
                Positioned(
                  left: 0,
                  top: 0,
                  bottom: 0,
                  child: Container(
                    width: 48,
                    height: 48,
                    margin: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                ),
                Transform.translate(
                  offset: Offset(_dragOffset, 0),
                  child: widget.child,
                ),
              ],
            ),
          );
        }
    );
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
