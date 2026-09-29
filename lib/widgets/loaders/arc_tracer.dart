// ArcTracer — an arc that draws itself around a track, then chases its tail away.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const ArcTracer()
//   ArcTracer(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class ArcTracer extends StatefulWidget {
  const ArcTracer({super.key, this.color, this.duration = const Duration(milliseconds: 2000)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<ArcTracer> createState() => _ArcTracerState();
}

class _ArcTracerState extends State<ArcTracer> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(ArcTracer oldWidget) {
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
    final track = dark ? const Color(0xFF27272A) : const Color(0xFFE4E4E7);
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {
          final t = _controller.value;
          return SizedBox.square(
            dimension: 40,
            child: CustomPaint(painter: _ArcTracerPainter(_keyframes(const [125, 0, -125], t), color, track)),
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

class _ArcTracerPainter extends CustomPainter {
  _ArcTracerPainter(this.offset, this.color, this.track);

  /// SVG-style dash offset on a 125-long dash (the circle's circumference is ~125.7).
  final double offset;
  final Color color;
  final Color track;

  static const _circumference = 2 * math.pi * 20;

  @override
  void paint(Canvas canvas, Size size) {
    final scale = size.width / 50;
    final rect = Rect.fromCircle(center: size.center(Offset.zero), radius: 20 * scale);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4 * scale
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, 0, 2 * math.pi, false, stroke..color = track);

    final start = math.max(0.0, -offset);
    final end = math.min(_circumference, 125 - offset);
    if (end - start < 0.5) return;
    canvas.drawArc(
      rect,
      start / _circumference * 2 * math.pi,
      (end - start) / _circumference * 2 * math.pi,
      false,
      stroke..color = color,
    );
  }

  @override
  bool shouldRepaint(_ArcTracerPainter old) =>
      old.offset != offset || old.color != color || old.track != track;
}
