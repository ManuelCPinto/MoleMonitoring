import 'dart:io';
import 'dart:convert';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:molemonitoringapp/utils/storage_helper.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/database_helper.dart';

class CameraApp extends StatefulWidget {
  final CameraDescription camera;
  const CameraApp({Key? key, required this.camera}) : super(key: key);

  @override
  State<CameraApp> createState() => _CameraAppState();
}

class _CameraAppState extends State<CameraApp> {
  late CameraController controller;
  late Future<void> _initializeControllerFuture;
  final ImagePicker _picker = ImagePicker();

  bool isPreview = false;
  String? capturedImagePath;

  // Dados do teu endpoint
  final String accessToken = "ya29.a0AXeO80Td_mDLnuATgXezCfteI6Hqv0ZhfM_7eHSClaSnVCI5tFeKa_4htGZfPiI4cdkQVZH1YyT6QRjztpJ6R7PijL6pY2PUZ9zlkumWs4t88bxQNm7c4NvdBPZjWM-YJoLC2PciPVt_xODv6adQMZPKQkmHL5Y7Hatw2rycO0JoKOwaCgYKAaMSARMSFQHGX2MiLJkhzFF464LRNAuko_AYKA0182";
  final String parseURI = 'https://europe-west3-aiplatform.googleapis.com/v1/projects/sic-molemonitoring/locations/europe-west3/endpoints/4241137405727342592:predict';

  @override
  void initState() {
    super.initState();
    controller = CameraController(
      widget.camera,
      ResolutionPreset.max,
      enableAudio: false,
    );
    _initializeControllerFuture = controller.initialize();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  /// Tirar foto => modo pré-visualização
  Future<void> _takePicture() async {
    try {
      await _initializeControllerFuture;
      final image = await controller.takePicture();
      final savedPath = await StorageHelper.saveImage(File(image.path));
      setState(() {
        capturedImagePath = savedPath;
        isPreview = true;
      });
    } catch (e) {
      debugPrint("Erro ao tirar foto: $e");
    }
  }

  /// Escolher da galeria => modo pré-visualização
  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        capturedImagePath = pickedFile.path;
        isPreview = true;
      });
    }
  }

  /// Envio ao endpoint
  Future<void> sendPredictionRequest(String imagePath) async {
    final uri = Uri.parse(parseURI);
    final originalBytes = await File(imagePath).readAsBytes();
    final int sizeThreshold = (1.5 * 1024 * 1024).toInt();

    List<int>? finalBytes;
    if (originalBytes.length > sizeThreshold) {
      debugPrint("Imagem maior que 1.5 MB, a comprimir...");
      final compressedBytes = await FlutterImageCompress.compressWithFile(
        imagePath,
        quality: 50,
        minWidth: 800,
        minHeight: 800,
        format: CompressFormat.jpeg,
      );
      finalBytes = compressedBytes;
    } else {
      finalBytes = originalBytes;
    }

    final base64Image = base64Encode(finalBytes!);
    final payload = json.encode({
      "instances": [
        {"image": base64Image}
      ]
    });

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: payload,
    );

    if (response.statusCode == 200) {
      final result = json.decode(response.body);
      print('Prediction result: $result');

      final predictionData = result['predictions'][0];
      final String prediction = predictionData['prediction'];
      final String confidence = predictionData['confidence'];
      final String timestamp = predictionData['timestamp'];
      final String processingTime = predictionData['processing_time'];
      final Map<String, dynamic> detailedPredictions = predictionData['detailed_predictions'];

      // Save the image locally.
      final savedImagePath = await StorageHelper.saveImage(File(imagePath));

      // Build the record to insert into the database.
      final predictionRecord = {
        'prediction': prediction,
        'confidence': confidence,
        'timestamp': timestamp,
        'processing_time': processingTime,
        'details': json.encode(detailedPredictions),
        'image_path': savedImagePath,
      };

      // Insert the prediction record into the database.
      await DatabaseHelper().insertPrediction(predictionRecord);

      print('Saved prediction: $predictionRecord');
    } else {
      print('Error: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Se isPreview => mostra imagem + botões "Process"/"Redo"
    // Senão => mostra câmara + botões "tirar foto"/"galeria"
    return isPreview ? _buildPreview() : _buildCamera();
  }

  /// Ecrã de câmara: fullscreen + botões "tirar foto" e "galeria"
  Widget _buildCamera() {
    return Stack(
      children: [
        // Câmera
        Positioned.fill(
          child: FutureBuilder<void>(
            future: _initializeControllerFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              } else if (snapshot.hasError) {
                return Center(child: Text("Camera error: ${snapshot.error}"));
              } else {
                return CameraPreview(controller);
              }
            },
          ),
        ),
        // Botões sobrepostos
        Positioned(
          bottom: 40,
          left: 0,
          right: 0,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Botão grande circular para tirar foto
              GestureDetector(
                onTap: _takePicture,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 5),
                  ),
                ),
              ),
              // Botão pequeno (galeria)
              Positioned(
                right: 80,
                child: GestureDetector(
                  onTap: _pickImage,
                  child: Container(
                    width: 50,
                    height: 50,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white,
                    ),
                    child: const Icon(
                      Icons.photo_library,
                      color: Colors.black87,
                      size: 28,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Ecrã de pré-visualização: Imagem + botões "Process" e "Redo"
  Widget _buildPreview() {
    return Stack(
      children: [
        // Imagem em fullscreen (cover)
        Positioned.fill(
          child: (capturedImagePath == null)
              ? const Center(
            child: Text(
              "Nenhuma imagem capturada",
              style: TextStyle(color: Colors.white),
            ),
          )
              : Image.file(
            File(capturedImagePath!),
            fit: BoxFit.cover,
          ),
        ),
        // Botões sobrepostos
        Positioned(
          bottom: 40,
          left: 0,
          right: 0,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Botão grande (Process)
              GestureDetector(
                onTap: () {
                  if (capturedImagePath != null) {
                    sendPredictionRequest(capturedImagePath!);
                  }
                },
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Color(0xFF005EB8),  // Fundo azul do botão grande
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.check,
                      color: Colors.white, // ícone branco p/ contraste
                      size: 32,
                    ),
                  ),
                ),
              ),
              // Botão pequeno (Redo)
              Positioned(
                right: 80,
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      capturedImagePath = null;
                      isPreview = false;
                    });
                  },
                  child: Container(
                    width: 50,
                    height: 50,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Color(0xFF005EB8),  // Fundo azul do botão pequeno
                    ),
                    child: const Center(
                      child: Icon(
                        Icons.refresh,
                        color: Colors.white, // ícone branco
                        size: 24,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
