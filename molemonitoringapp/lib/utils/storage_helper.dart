import 'dart:io';
import 'package:path_provider/path_provider.dart';

class StorageHelper {
  static Future<String> saveImage(File imageFile) async {
    final directory = await getApplicationDocumentsDirectory();
    final path = '${directory.path}/mole_images';
    await Directory(path).create(recursive: true);

    final fileName = '${DateTime.now().millisecondsSinceEpoch}.jpg';
    final savedImage = await imageFile.copy('$path/$fileName');

    return savedImage.path;
  }
}
