// NewtonsCradle — four balls clacking like a Newton's cradle.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const NewtonsCradle()
//   NewtonsCradle(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class NewtonsCradle extends StatefulWidget {
  const NewtonsCradle({super.key, this.color, this.duration = const Duration(milliseconds: 1500)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<NewtonsCradle> createState() => _NewtonsCradleState();
}

class _NewtonsCradleState extends State<NewtonsCradle> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(NewtonsCradle oldWidget) {
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
          Widget swing(double degrees) => Transform(
            alignment: Alignment.topCenter,
            // Pivot on an invisible string above the ball so it swings in an arc.
            origin: const Offset(0, -20),
            transform: Matrix4.rotationZ(degrees * math.pi / 180),
            child: _dot(12, color),
          );
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                swing(_keyframes(const [25, 0, 0, 0, 0, 25], t)),
                const SizedBox(width: 2),
                _dot(12, color),
                const SizedBox(width: 2),
                _dot(12, color),
                const SizedBox(width: 2),
                swing(_keyframes(const [0, 0, 0, -25, 0, 0], t)),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t, [Curve curve = Curves.easeInOut]) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = math.min(x.floor(), segments - 1);
  return values[i] + (values[i + 1] - values[i]) * curve.transform(x - i);
}

Widget _dot(double size, Color color) => Container(
  width: size,
  height: size,
  decoration: BoxDecoration(color: color, shape: BoxShape.circle),
);
