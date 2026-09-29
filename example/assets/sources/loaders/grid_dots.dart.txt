// GridDots — a 3x3 grid pulsing diagonally.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const GridDots()
//   GridDots(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class GridDots extends StatefulWidget {
  const GridDots({super.key, this.color, this.duration = const Duration(milliseconds: 1500)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<GridDots> createState() => _GridDotsState();
}

class _GridDotsState extends State<GridDots> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(GridDots oldWidget) {
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
          return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var row = 0; row < 3; row++)
                Padding(
                  padding: EdgeInsets.only(top: row == 0 ? 0 : 6),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      for (var col = 0; col < 3; col++)
                        Padding(
                          padding: EdgeInsets.only(left: col == 0 ? 0 : 6),
                          child: Opacity(
                            opacity: _keyframes(const [1, 0.3, 1], _phase(t, (row + col) * 0.2 / 1.5)),
                            child: Transform.scale(
                              scale: _keyframes(const [1, 0.5, 1], _phase(t, (row + col) * 0.2 / 1.5)),
                              child: _dot(10, color),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
            ],
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
