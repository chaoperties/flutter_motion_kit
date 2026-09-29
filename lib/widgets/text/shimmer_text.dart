// ShimmerText — a soft gradient highlight that gently pulses.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Shimmer Text" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const ShimmerText('SHIMMER TEXT')
//   ShimmerText('Hello world', color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class ShimmerText extends StatefulWidget {
  const ShimmerText(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.duration = const Duration(milliseconds: 2000),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to white or black for the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  @override
  State<ShimmerText> createState() => _ShimmerTextState();
}

class _ShimmerTextState extends State<ShimmerText>
    with SingleTickerProviderStateMixin {
  late final Ticker _ticker = createTicker(_onTick);
  // Seconds since the animation started (negative while waiting for the delay).
  late final _time = ValueNotifier<double>(0);

  @override
  void initState() {
    super.initState();
    _ticker.start();
  }

  void _onTick(Duration elapsed) => _time.value = elapsed.inMicroseconds / 1e6;

  @override
  void dispose() {
    _ticker.dispose();
    _time.dispose();
    super.dispose();
  }

  /// Position (0..1) in the loop of unit [i]; each unit starts at once.
  double _loop(double time, int i) {
    final local = time - i * 0;
    final length = _seconds(widget.duration);
    if (local <= 0 || length <= 0) return 0;
    return local / length % 1.0;
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w800,
            color: dark ? Colors.white : Colors.black,
          ),
        )
        .merge(widget.style);
    if (widget.color != null) style = style.copyWith(color: widget.color);

    return Semantics(
      label: widget.text,
      child: ExcludeSemantics(
        child: RepaintBoundary(
          child: ValueListenableBuilder<double>(
            valueListenable: _time,
            builder: (context, t, _) {
              final time = t;
              return _unit(context, widget.text, style, time, 0);
            },
          ),
        ),
      ),
    );
  }

  /// One copy of the text at [time] seconds.
  Widget _unit(
    BuildContext context,
    String text,
    TextStyle style,
    double time,
    int i,
  ) {
    final u = _loop(time, i);
    final dark = Theme.of(context).brightness == Brightness.dark;
    final edge =
        widget.color?.withValues(alpha: 0.6) ??
        (dark ? const Color(0xFFA3A3A3) : const Color(0xFF525252));
    // Tailwind's animate-pulse on a neutral-bright-neutral gradient.
    return Opacity(
      opacity: _keyframes(const [1, 0.5, 1], u, const Cubic(0.4, 0, 0.6, 1)),
      child: ShaderMask(
        blendMode: BlendMode.srcIn,
        shaderCallback: (rect) =>
            LinearGradient(colors: [edge, style.color!, edge])
                .createShader(rect),
        child: Text(text, style: style, textAlign: TextAlign.center),
      ),
    );
  }
}

double _seconds(Duration d) => d.inMicroseconds / 1e6;

/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(
  List<double> values,
  double t, [
  Curve curve = Curves.easeInOut,
]) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = math.min(x.floor(), segments - 1);
  return values[i] + (values[i + 1] - values[i]) * curve.transform(x - i);
}
