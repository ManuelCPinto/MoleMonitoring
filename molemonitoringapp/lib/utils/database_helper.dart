import 'dart:async';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;

  static Database? _database;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    Directory documentsDirectory = await getApplicationDocumentsDirectory();
    String path = join(documentsDirectory.path, "predictions.db");

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prediction TEXT,
            confidence TEXT,
            details TEXT,
            processing_time TEXT
          )
        ''');
      },
    );
  }

  Future<int> insertPrediction(Map<String, dynamic> prediction) async {
    Database db = await database;
    return await db.insert("predictions", prediction);
  }

  Future<List<Map<String, dynamic>>> getPredictions() async {
    Database db = await database;
    return await db.query("predictions", orderBy: "id DESC");
  }

  Future<int> deleteAllPredictions() async {
    Database db = await database;
    return await db.delete("predictions");
  }
}
