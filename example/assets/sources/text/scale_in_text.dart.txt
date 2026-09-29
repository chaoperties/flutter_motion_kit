// ScaleInText — the text springs up from half size.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Scale In Text" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const ScaleInText('SCALE IN TEXT')
//   ScaleInText('Hello world', style: TextStyle(fontSize: 48), delay: Duration(milliseconds: 300))
//
// Plays once when first shown, and again whenever `text` changes. Give it a new
// Key to replay it. With reduced motion turned on, it shows the final state.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/scheduler.dart';

class ScaleInText extends StatefulWidget {
  const ScaleInText(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.delay = Duration.zero,
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to white or black for the current light/dark theme.
  final Color? color;

  /// Wait before the animation starts.
  final Duration delay;

  @override
  State<ScaleInText> createState() => _ScaleInTextState();
}

class _ScaleInTextState extends State<ScaleInText>
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
  void didUpdateWidget(covariant ScaleInText oldWidget) {
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

  double get _end => math.max(0, 1 - 1) * 0 + 0.640;

  // Spring(stiffness: 400, damping: 25); it has settled after 0.640s.
  static final _spring = SpringSimulation(
    const SpringDescription(mass: 1, stiffness: 400, damping: 25),
    0,
    1,
    0,
  );

  double _sprung(double time, int i) {
    final local = time - i * 0;
    if (local <= 0) return 0;
    if (local >= 0.640) return 1;
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
    final p = _sprung(time, i);
    Widget child = Text(text, style: style);
    final scale = _lerp(0.5, 1, p);
    child = Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()..scaleByDouble(scale, scale, 1, 1),
      child: child,
    );
    child = Opacity(opacity: _lerp(0, 1, p).clamp(0.0, 1.0), child: child);
    return child;
  }
}

double _seconds(Duration d) => d.inMicroseconds / 1e6;

double _lerp(double a, double b, double t) => a + (b - a) * t;
