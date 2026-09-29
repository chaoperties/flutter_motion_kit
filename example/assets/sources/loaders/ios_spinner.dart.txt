// IOSSpinner — the thin twelve-spoke iOS activity indicator.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const IOSSpinner()
//   IOSSpinner(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class IOSSpinner extends StatefulWidget {
  const IOSSpinner({super.key, this.color, this.duration = const Duration(milliseconds: 1000)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<IOSSpinner> createState() => _IOSSpinnerState();
}

class _IOSSpinnerState extends State<IOSSpinner> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(IOSSpinner oldWidget) {
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
            child: Stack(
              children: [
                for (var i = 0; i < 12; i++)
                  Positioned.fill(
                    child: Transform.rotate(
                      angle: i * math.pi / 6,
                      child: Align(
                        alignment: Alignment.topCenter,
                        child: Opacity(
                          opacity: _keyframes(const [1, 0.2], _phase(t, i / 12), Curves.linear),
                          child: Container(
                            width: 2,
                            height: 7,
                            decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(1)),
                          ),
                        ),
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
