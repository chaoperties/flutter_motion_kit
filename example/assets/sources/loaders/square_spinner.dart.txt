// SquareSpinner — a square outline ticking round a quarter turn at a time.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const SquareSpinner()
//   SquareSpinner(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class SquareSpinner extends StatefulWidget {
  const SquareSpinner({super.key, this.color, this.duration = const Duration(milliseconds: 600)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<SquareSpinner> createState() => _SquareSpinnerState();
}

class _SquareSpinnerState extends State<SquareSpinner> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(SquareSpinner oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.duration != widget.duration) {
      _controller
        ..duration = widget.duration
        ..repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final color = widget.color ?? (dark ? Colors.white : const Color(0xFF27272A));
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {
          final t = _controller.value;
          return Transform.rotate(
            angle: Curves.easeInOut.transform(t) * math.pi / 2,
            child: Container(
              width: 32,
              height: 32,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                border: Border.all(color: dark ? const Color(0xFF3F3F46) : color, width: 2),
              ),
              child: Container(width: 8, height: 8, color: color),
            ),
          );
        },
      ),
    );
  }
}
