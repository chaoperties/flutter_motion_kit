// TypewriterText — typed out behind a cursor.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Typewriter Text" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const TypewriterText('TYPEWRITER')
//   TypewriterText('Hello world', style: TextStyle(fontSize: 48), delay: Duration(milliseconds: 300))
//
// Plays once when first shown, and again whenever `text` changes. Give it a new
// Key to replay it. With reduced motion turned on, it shows the final state.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class TypewriterText extends StatefulWidget {
  const TypewriterText(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.delay = Duration.zero,
    this.duration = const Duration(milliseconds: 1200),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to emerald for the current light/dark theme.
  final Color? color;

  /// Wait before the animation starts.
  final Duration delay;

  /// Length of the animation.
  final Duration duration;

  @override
  State<TypewriterText> createState() => _TypewriterTextState();
}

class _TypewriterTextState extends State<TypewriterText>
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
  void didUpdateWidget(covariant TypewriterText oldWidget) {
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

  double get _end => math.max(0, 1 - 1) * 0 + _seconds(widget.duration);

  /// Linear progress (0..1) of unit [i] at [time] seconds.
  double _linear(double time, int i) {
    final length = _seconds(widget.duration);
    if (length <= 0) return 1;
    return ((time - i * 0) / length).clamp(0.0, 1.0);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: dark ? const Color(0xFF34D399) : const Color(0xFF059669),
            fontFamily: 'monospace',
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
    final t = _linear(time, i);
    final p = Curves.easeInOut.transform(t);
    return DecoratedBox(
      // The cursor is the right border, so it rides along the typed edge.
      decoration: BoxDecoration(
        border: Border(
          right: BorderSide(
            color: style.color ?? const Color(0xFF34D399),
            width: 2,
          ),
        ),
      ),
      child: ClipRect(
        child: Align(
          alignment: Alignment.centerLeft,
          widthFactor: p.clamp(0.0, 1.0),
          child: Text(text, style: style, maxLines: 1, softWrap: false),
        ),
      ),
    );
  }
}

double _seconds(Duration d) => d.inMicroseconds / 1e6;
