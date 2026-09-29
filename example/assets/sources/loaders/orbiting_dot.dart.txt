// OrbitingDot — a dot orbiting a faint ring.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const OrbitingDot()
//   OrbitingDot(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class OrbitingDot extends StatefulWidget {
  const OrbitingDot({super.key, this.color, this.duration = const Duration(milliseconds: 2000)});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<OrbitingDot> createState() => _OrbitingDotState();
}

class _OrbitingDotState extends State<OrbitingDot> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(OrbitingDot oldWidget) {
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
            child: Stack(
              alignment: Alignment.center,
              clipBehavior: Clip.none,
              children: [
                _dot(8, dark ? const Color(0xFF3F3F46) : const Color(0xFFD4D4D8)),
                Transform.rotate(
                  angle: t * 2 * math.pi,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: track),
                        ),
                      ),
                      Positioned(left: 14, top: -6, child: _dot(12, color)),
                    ],
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

Widget _dot(double size, Color color) => Container(
  width: size,
  height: size,
  decoration: BoxDecoration(color: color, shape: BoxShape.circle),
);
