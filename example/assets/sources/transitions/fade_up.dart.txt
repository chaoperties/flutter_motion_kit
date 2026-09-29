// FadeUp — fades a widget in while it drifts up into place.
//
// Copy this file into your project. It depends only on Flutter itself.
//
// Usage:
//   FadeUp(child: Text('Hello'))
//
//   // Staggered list:
//   for (var i = 0; i < items.length; i++)
//     FadeUp(delay: Duration(milliseconds: 80 * i), child: items[i])

import 'dart:async';
import 'dart:ui' show ImageFilter;

import 'package:flutter/material.dart';

class FadeUp extends StatefulWidget {
  const FadeUp({
    super.key,
    required this.child,
    this.delay = Duration.zero,
    this.duration = const Duration(milliseconds: 600),
    this.distance = 24,
    this.blur = false,
    this.curve = Curves.easeOutCubic,
  });

  final Widget child;

  /// Wait before starting. Use increasing delays to stagger siblings.
  final Duration delay;

  final Duration duration;

  /// How far below its final position the child starts, in pixels.
  final double distance;

  /// Also starts blurred and slightly smaller, then pulls into focus.
  final bool blur;

  final Curve curve;

  @override
  State<FadeUp> createState() => _FadeUpState();
}

class _FadeUpState extends State<FadeUp> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration);
  late final Animation<double> _t = CurvedAnimation(parent: _controller, curve: widget.curve);
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    if (widget.delay == Duration.zero) {
      _controller.forward();
    } else {
      _timer = Timer(widget.delay, _controller.forward);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _t,
      child: widget.child,
      builder: (context, child) {
        final t = _t.value;
        final scale = widget.blur ? 0.96 + 0.04 * t : 1.0;
        if (widget.blur) {
          // Keep ImageFiltered in the tree (just disabled at the end) so the child never remounts.
          final sigma = 8 * (1 - t).clamp(0.0, 1.0);
          child = ImageFiltered(
            enabled: t < 1,
            imageFilter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
            child: child,
          );
        }
        return Opacity(
          opacity: t.clamp(0.0, 1.0),
          child: Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
              ..translateByDouble(0, widget.distance * (1 - t), 0, 1)
              ..scaleByDouble(scale, scale, 1, 1),
            child: child,
          ),
        );
      },
    );
  }
}
