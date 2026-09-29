// FloatWord — words bob gently up and down.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Float Word" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const FloatWord('Design Motion Amicro')
//   FloatWord('Hello world', color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class FloatWord extends StatefulWidget {
  const FloatWord(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.duration = const Duration(milliseconds: 2400),
    this.stagger = const Duration(milliseconds: 200),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to cyan for the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  /// How far each word runs behind the one before it.
  final Duration stagger;

  @override
  State<FloatWord> createState() => _FloatWordState();
}

class _FloatWordState extends State<FloatWord>
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

  /// Position (0..1) in the loop of unit [i]; each unit starts [stagger] after the one before.
  double _loop(double time, int i) {
    final local = time - i * _seconds(widget.stagger);
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
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: dark ? const Color(0xFF22D3EE) : const Color(0xFF0891B2),
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
              return _splitWords(
                widget.text,
                (style.fontSize ?? 20) * 0.4,
                (text, i) => _unit(context, text, style, time, i),
              );
            },
          ),
        ),
      ),
    );
  }

  /// One word at [time] seconds.
  Widget _unit(
    BuildContext context,
    String text,
    TextStyle style,
    double time,
    int i,
  ) {
    final u = _loop(time, i);
    Widget child = Text(text, style: style);
    child = Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..translateByDouble(0, _keyframes(const [0, -8, 0], u), 0, 1),
      child: child,
    );
    return child;
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

List<String> _words(String text) => [
  for (final w in text.split(' '))
    if (w.isNotEmpty) w,
];

/// Builds [text] one word at a time with a gap of [gap] between words.
Widget _splitWords(
  String text,
  double gap,
  Widget Function(String unit, int index) unit,
) {
  final words = _words(text);
  return Wrap(
    alignment: WrapAlignment.center,
    crossAxisAlignment: WrapCrossAlignment.center,
    spacing: gap,
    children: [for (var i = 0; i < words.length; i++) unit(words[i], i)],
  );
}
