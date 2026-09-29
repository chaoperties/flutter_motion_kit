// ScaleInChar — characters spring up from nothing.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Scale In Char" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const ScaleInChar('AMICRO UI')
//   ScaleInChar('Hello world', style: TextStyle(fontSize: 48), stagger: Duration(milliseconds: 80))
//
// Plays once when first shown, and again whenever `text` changes. Give it a new
// Key to replay it. With reduced motion turned on, it shows the final state.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/scheduler.dart';

class ScaleInChar extends StatefulWidget {
  const ScaleInChar(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.delay = Duration.zero,
    this.stagger = const Duration(milliseconds: 40),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to white or black for the current light/dark theme.
  final Color? color;

  /// Wait before the animation starts.
  final Duration delay;

  /// Time between one character starting and the next.
  final Duration stagger;

  @override
  State<ScaleInChar> createState() => _ScaleInCharState();
}

class _ScaleInCharState extends State<ScaleInChar>
    with SingleTickerProviderStateMixin {
  late final Ticker _ticker = createTicker(_onTick);
  // Seconds since the animation started (negative while waiting for the delay).
  late final _time = ValueNotifier<double>(-_seconds(widget.delay));

  @override
  void initState() {
    super.initState();
    _ticker.start();
  }

  void _onTick(Duration elapsed) {
    _time.value = elapsed.inMicroseconds / 1e6 - _seconds(widget.delay);
    if (_time.value >= _end) _ticker.stop();
  }

  @override
  void didUpdateWidget(covariant ScaleInChar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text != widget.text) {
      _ticker.stop();
      _time.value = -_seconds(widget.delay);
      _ticker.start();
    }
  }

  @override
  void dispose() {
    _ticker.dispose();
    _time.dispose();
    super.dispose();
  }

  double get _end =>
      math.max(0, widget.text.characters.length - 1) *
          _seconds(widget.stagger) +
      0.727;

  // Spring(stiffness: 450, damping: 22); it has settled after 0.727s.
  static final _spring = SpringSimulation(
    const SpringDescription(mass: 1, stiffness: 450, damping: 22),
    0,
    1,
    0,
  );

  double _sprung(double time, int i) {
    final local = time - i * _seconds(widget.stagger);
    if (local <= 0) return 0;
    if (local >= 0.727) return 1;
    return _spring.x(local);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: dark ? Colors.white : Colors.black,
          ),
        )
        .merge(widget.style);
    if (widget.color != null) style = style.copyWith(color: widget.color);
    // With reduced motion, jump straight to the end.
    final still = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return Semantics(
      label: widget.text,
      child: ExcludeSemantics(
        child: RepaintBoundary(
          child: ValueListenableBuilder<double>(
            valueListenable: _time,
            builder: (context, t, _) {
              final time = still ? double.infinity : t;
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
    final p = _sprung(time, i);
    Widget child = Text(text, style: style);
    final scale = _lerp(0, 1, p);
    child = Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()..scaleByDouble(scale, scale, 1, 1),
      child: child,
    );
    return child;
  }
}

double _seconds(Duration d) => d.inMicroseconds / 1e6;

double _lerp(double a, double b, double t) => a + (b - a) * t;

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
