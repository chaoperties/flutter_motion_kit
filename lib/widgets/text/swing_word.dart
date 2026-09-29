// SwingWord — words swing down into place like a pendulum.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Swing Word" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const SwingWord('Design Motion Amicro')
//   SwingWord('Hello world', style: TextStyle(fontSize: 48), stagger: Duration(milliseconds: 80))
//
// Plays once when first shown, and again whenever `text` changes. Give it a new
// Key to replay it. With reduced motion turned on, it shows the final state.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/scheduler.dart';

class SwingWord extends StatefulWidget {
  const SwingWord(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.delay = Duration.zero,
    this.stagger = const Duration(milliseconds: 120),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to purple for the current light/dark theme.
  final Color? color;

  /// Wait before the animation starts.
  final Duration delay;

  /// Time between one word starting and the next.
  final Duration stagger;

  @override
  State<SwingWord> createState() => _SwingWordState();
}

class _SwingWordState extends State<SwingWord>
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
  void didUpdateWidget(covariant SwingWord oldWidget) {
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
      math.max(0, _words(widget.text).length - 1) * _seconds(widget.stagger) +
      0.889;

  // Spring(stiffness: 350, damping: 18); it has settled after 0.889s.
  static final _spring = SpringSimulation(
    const SpringDescription(mass: 1, stiffness: 350, damping: 18),
    0,
    1,
    0,
  );

  double _sprung(double time, int i) {
    final local = time - i * _seconds(widget.stagger);
    if (local <= 0) return 0;
    if (local >= 0.889) return 1;
    return _spring.x(local);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: dark ? const Color(0xFFC084FC) : const Color(0xFF9333EA),
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
    final p = _sprung(time, i);
    Widget child = Text(text, style: style);
    child = Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..setEntry(3, 2, -1 / 800)
        ..rotateX(_lerp(-90, 0, p) * math.pi / 180),
      child: child,
    );
    child = Opacity(opacity: _lerp(0, 1, p).clamp(0.0, 1.0), child: child);
    return child;
  }
}

double _seconds(Duration d) => d.inMicroseconds / 1e6;

double _lerp(double a, double b, double t) => a + (b - a) * t;

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
