// SlideDownWord — words drop down from a hidden top edge.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Slide Down Word" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const SlideDownWord('Design Motion Amicro')
//   SlideDownWord('Hello world', style: TextStyle(fontSize: 48), stagger: Duration(milliseconds: 80))
//
// Plays once when first shown, and again whenever `text` changes. Give it a new
// Key to replay it. With reduced motion turned on, it shows the final state.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class SlideDownWord extends StatefulWidget {
  const SlideDownWord(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.delay = Duration.zero,
    this.duration = const Duration(milliseconds: 500),
    this.stagger = const Duration(milliseconds: 100),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to white or black for the current light/dark theme.
  final Color? color;

  /// Wait before the animation starts.
  final Duration delay;

  /// Length of the animation of each word.
  final Duration duration;

  /// Time between one word starting and the next.
  final Duration stagger;

  @override
  State<SlideDownWord> createState() => _SlideDownWordState();
}

class _SlideDownWordState extends State<SlideDownWord>
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
  void didUpdateWidget(covariant SlideDownWord oldWidget) {
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
      _seconds(widget.duration);

  /// Linear progress (0..1) of unit [i] at [time] seconds.
  double _linear(double time, int i) {
    final length = _seconds(widget.duration);
    if (length <= 0) return 1;
    return ((time - i * _seconds(widget.stagger)) / length).clamp(0.0, 1.0);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 20,
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
    final t = _linear(time, i);
    final p = const Cubic(0.16, 1, 0.3, 1).transform(t);
    Widget child = Text(text, style: style);
    child = FractionalTranslation(
      translation: Offset(0, _lerp(-1, 0, p)),
      child: child,
    );
    child = ClipRect(child: child);
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
