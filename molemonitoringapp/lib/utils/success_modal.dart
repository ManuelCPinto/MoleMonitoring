import 'package:flutter/material.dart';

Future<void> showSuccessModal(BuildContext context) {
  return showGeneralDialog(
    context: context,
    barrierDismissible: false,
    barrierColor: Colors.white,
    transitionDuration: const Duration(milliseconds: 300),
    pageBuilder: (context, animation, secondaryAnimation) {
      return const _SuccessModal();
    },
  );
}

class _SuccessModal extends StatefulWidget {
  const _SuccessModal({super.key});

  @override
  State<_SuccessModal> createState() => _SuccessModalState();
}

class _SuccessModalState extends State<_SuccessModal> {
  bool _showDone = false;

  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 3), () {
      setState(() {
        _showDone = true;
      });
      Future.delayed(const Duration(seconds: 1), () {
        Navigator.of(context).pop();
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: _showDone
              ? Column(
                  key: const ValueKey('done'),
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(
                      Icons.check_circle,
                      color: Colors.green,
                      size: 100,
                    ),
                    SizedBox(height: 16),
                    Text(
                      "Done!",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                )
              : Column(
                  key: const ValueKey('processing'),
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text(
                      "Processing...",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}
