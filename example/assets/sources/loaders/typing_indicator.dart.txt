// TypingIndicator — a chat bubble with three bobbing dots.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const TypingIndicator()
//   TypingIndicator(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key, this.color, this.duration = const Duration(milliseconds: 600)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(TypingIndicator oldWidget) {
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
    final color = widget.color ?? (dark ? const Color(0xFFA1A1AA) : const Color(0xFF71717A));
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {
          final t = _controller.value;
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: dark ? const Color(0xFF27272A) : const Color(0xFFF4F4F5),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                for (var i = 0; i < 3; i++)
                  Padding(
                    padding: EdgeInsets.only(left: i == 0 ? 0 : 4),
                    child: Transform.translate(
                      offset: Offset(0, _keyframes(const [0, -4, 0], _phase(t, i * 0.15 / 0.6))),
                      child: _dot(6, color),
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
