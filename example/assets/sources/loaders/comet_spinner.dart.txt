// CometSpinner — a ring with a comet tail sweeping around.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const CometSpinner()
//   CometSpinner(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class CometSpinner extends StatefulWidget {
  const CometSpinner({super.key, this.color, this.duration = const Duration(milliseconds: 1000)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<CometSpinner> createState() => _CometSpinnerState();
}

class _CometSpinnerState extends State<CometSpinner> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(CometSpinner oldWidget) {
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
          return SizedBox.square(dimension: 40, child: CustomPaint(painter: _CometPainter(t, color, track)));
        },
      ),
    );
  }
}

class _CometPainter extends CustomPainter {
  _CometPainter(this.t, this.color, this.track);

  final double t;
  final Color color;
  final Color track;

  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero);
    final r = size.width / 2 - 2;
    canvas.drawCircle(
      c,
      size.width / 2 - 0.5,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = track,
    );
    final sweep = SweepGradient(
      colors: [color.withValues(alpha: 0), color.withValues(alpha: 0.1), color],
      stops: const [0, 0.6, 1],
      transform: GradientRotation(t * 2 * math.pi - math.pi / 2),
    );
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..shader = sweep.createShader(Rect.fromCircle(center: c, radius: r)),
    );
  }

  @override
  bool shouldRepaint(_CometPainter old) => old.t != t || old.color != color || old.track != track;
}
