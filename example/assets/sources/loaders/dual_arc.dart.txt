// DualArc — two opposite arcs spinning and breathing.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const DualArc()
//   DualArc(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class DualArc extends StatefulWidget {
  const DualArc({super.key, this.color, this.duration = const Duration(milliseconds: 1200)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<DualArc> createState() => _DualArcState();
}

class _DualArcState extends State<DualArc> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(DualArc oldWidget) {
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
          return SizedBox.square(
            dimension: 32,
            child: Transform.rotate(
              angle: t * 2 * math.pi,
              child: Transform.scale(
                scale: _keyframes(const [1, 0.82, 1], t),
                child: CustomPaint(painter: _DualArcPainter(color)),
              ),
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

class _DualArcPainter extends CustomPainter {
  _DualArcPainter(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(1);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = color;
    // Top and bottom quarters, like a circle with only border-top and border-bottom.
    canvas.drawArc(rect, -3 * math.pi / 4, math.pi / 2, false, paint);
    canvas.drawArc(rect, math.pi / 4, math.pi / 2, false, paint);
  }

  @override
  bool shouldRepaint(_DualArcPainter old) => old.color != color;
}
