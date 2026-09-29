// GlowText — text with a softly breathing glow.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Glow Text" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const GlowText('GLOW TEXT')
//   GlowText('Hello world', color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class GlowText extends StatefulWidget {
  const GlowText(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.duration = const Duration(milliseconds: 2000),
    this.glowColor,
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to indigo for the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  /// Colour of the glow; defaults to indigo.
  final Color? glowColor;

  @override
  State<GlowText> createState() => _GlowTextState();
}

class _GlowTextState extends State<GlowText>
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
            fontSize: 30,
            fontWeight: FontWeight.w900,
            color: dark ? const Color(0xFFA5B4FC) : const Color(0xFF4F46E5),
            letterSpacing: -0.025 * 30,
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
    // CSS text-shadow blurs of 10px → 25px (dark) or 20px (light), converted to Flutter's blurRadius.
    final dark = Theme.of(context).brightness == Brightness.dark;
    final glow =
        widget.glowColor ??
        (dark ? const Color(0xFF6366F1) : const Color(0xFF4F46E5));
    final alpha = dark ? const [0.5, 0.9, 0.5] : const [0.3, 0.6, 0.3];
    final blur = dark ? const [7.8, 20.8, 7.8] : const [7.8, 16.5, 7.8];
    return Text(
      text,
      textAlign: TextAlign.center,
      style: style.copyWith(
        shadows: [
          Shadow(
            color: glow.withValues(alpha: _keyframes(alpha, u)),
            blurRadius: _keyframes(blur, u),
          ),
        ],
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
