// RippleEffect — rings rippling out from a centre dot.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const RippleEffect()
//   RippleEffect(color: Colors.teal)

import 'package:flutter/material.dart';

class RippleEffect extends StatefulWidget {
  const RippleEffect({super.key, this.color, this.duration = const Duration(milliseconds: 2200)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<RippleEffect> createState() => _RippleEffectState();
}

class _RippleEffectState extends State<RippleEffect> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(RippleEffect oldWidget) {
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
              alignment: Alignment.center,
              clipBehavior: Clip.none,
              children: [
                _dot(10, color),
                for (var i = 0; i < 3; i++)
                  Opacity(
                    opacity: 0.8 * (1 - Curves.easeOut.transform(_phase(t, i * 0.7 / 2.2))),
                    child: Transform.scale(
                      scale: 0.3 + 1.3 * Curves.easeOut.transform(_phase(t, i * 0.7 / 2.2)),
                      child: Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: color),
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

Widget _dot(double size, Color color) => Container(
  width: size,
  height: size,
  decoration: BoxDecoration(color: color, shape: BoxShape.circle),
);
