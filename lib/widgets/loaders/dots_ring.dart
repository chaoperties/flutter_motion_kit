// DotsRing — eight dots in a circle pulsing around.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const DotsRing()
//   DotsRing(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class DotsRing extends StatefulWidget {
  const DotsRing({super.key, this.color, this.duration = const Duration(milliseconds: 1500)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<DotsRing> createState() => _DotsRingState();
}

class _DotsRingState extends State<DotsRing> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(DotsRing oldWidget) {
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
            dimension: 48,
            child: Stack(
              children: [
                for (var i = 0; i < 8; i++)
                  Positioned(
                    left: 24 + 20 * math.sin(i * math.pi / 4) - 4,
                    top: 24 - 20 * math.cos(i * math.pi / 4) - 4,
                    child: Opacity(
                      opacity: _keyframes(const [1, 0.3, 1], _phase(t, i * 0.15 / 1.5)),
                      child: Transform.scale(
                        scale: _keyframes(const [1, 0.5, 1], _phase(t, i * 0.15 / 1.5)),
                        child: _dot(8, color),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// Position in the loop for an element that starts [shift] (0..1 of a loop) late.
double _phase(double t, double shift) => (t - shift) % 1.0;

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
