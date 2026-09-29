// TextShimmer — text with a shine sweeping across it.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const TextShimmer()
//   TextShimmer(color: Colors.teal)

import 'package:flutter/material.dart';

class TextShimmer extends StatefulWidget {
  const TextShimmer({
    super.key,
    this.color,
    this.duration = const Duration(milliseconds: 1500),
    this.text = 'Thinking',
  });

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  /// The text to shimmer.
  final String text;

  @override
  State<TextShimmer> createState() => _TextShimmerState();
}

class _TextShimmerState extends State<TextShimmer> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget(TextShimmer oldWidget) {
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
          final style = TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: color);
          return Stack(
            children: [
              Text(widget.text, style: style.copyWith(color: color.withValues(alpha: 0.25))),
              ShaderMask(
                blendMode: BlendMode.dstIn,
                shaderCallback: (rect) {
                  // A band twice as wide as the text slides left to right; its opaque middle is the shine.
                  final w = rect.width;
                  return const LinearGradient(
                    colors: [Color(0x00000000), Color(0xFF000000), Color(0x00000000)],
                  ).createShader(Rect.fromLTWH(-w + 2 * w * t, 0, 2 * w, rect.height));
                },
                child: Text(widget.text, style: style),
              ),
            ],
          );
        },
      ),
    );
  }
}
