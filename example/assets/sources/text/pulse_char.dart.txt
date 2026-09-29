// PulseChar — characters breathe in and out of view.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Pulse Char" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const PulseChar('AMICRO UI')
//   PulseChar('Hello world', color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class PulseChar extends StatefulWidget {
  const PulseChar(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.duration = const Duration(milliseconds: 1500),
    this.stagger = const Duration(milliseconds: 80),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to emerald for the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;

  /// How far each character runs behind the one before it.
  final Duration stagger;

  @override
  State<PulseChar> createState() => _PulseCharState();
}

class _PulseCharState extends State<PulseChar>
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
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: dark ? const Color(0xFF34D399) : const Color(0xFF059669),
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
              return _splitChars(
                widget.text,
                (text, i) => _unit(context, text, style, time, i),
              );
            },
          ),
        ),
      ),
    );
  }

  /// One character at [time] seconds.
  Widget _unit(
    BuildContext context,
    String text,
    TextStyle style,
    double time,
    int i,
  ) {
    final u = _loop(time, i);
    Widget child = Text(text, style: style);
    child = Opacity(
      opacity: _keyframes(const [0.3, 1, 0.3], u).clamp(0.0, 1.0),
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

/// Builds [text] one grapheme at a time (so emoji and Thai vowels stay whole),
/// keeping each word on one line and numbering units in reading order.
Widget _splitChars(String text, Widget Function(String unit, int index) unit) {
  final words = text.split(' ');
  final children = <Widget>[];
  var i = 0;
  for (var w = 0; w < words.length; w++) {
    final units = <Widget>[for (final c in words[w].characters) unit(c, i++)];
    // A non-breaking space, so the gap keeps its width at the end of a line.
    if (w < words.length - 1) units.add(unit('\u00A0', i++));
    children.add(Row(mainAxisSize: MainAxisSize.min, children: units));
  }
  return Wrap(
    alignment: WrapAlignment.center,
    crossAxisAlignment: WrapCrossAlignment.center,
    children: children,
  );
}
