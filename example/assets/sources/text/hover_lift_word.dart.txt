// HoverLiftWord — words lift under the pointer.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Hover Lift Word" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const HoverLiftWord('Design Motion Amicro')
//   HoverLiftWord('Hello world', style: TextStyle(fontSize: 48))
//
// Reacts to a mouse pointer; on touch screens the text simply stays still.

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class HoverLiftWord extends StatelessWidget {
  const HoverLiftWord(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.hoverColor = const Color(0xFF3B82F6),
  });

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to white or black for the current light/dark theme.
  final Color? color;

  /// Colour a unit turns while the pointer is over it.
  final Color hoverColor;

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
        .merge(this.style);
    if (color != null) style = style.copyWith(color: color);
    return Semantics(
      label: text,
      child: ExcludeSemantics(
        child: _splitWords(
          text,
          (style.fontSize ?? 20) * 0.4,
          (unit, _) =>
              _HoverUnit(text: unit, style: style, hoverColor: hoverColor),
        ),
      ),
    );
  }
}

/// One word that springs towards its hover pose.
class _HoverUnit extends StatefulWidget {
  const _HoverUnit({
    required this.text,
    required this.style,
    required this.hoverColor,
  });

  final String text;
  final TextStyle style;
  final Color hoverColor;

  @override
  State<_HoverUnit> createState() => _HoverUnitState();
}

class _HoverUnitState extends State<_HoverUnit>
    with SingleTickerProviderStateMixin {
  // 0 = resting, 1 = hovered; the spring may overshoot a little.
  late final AnimationController _hover = AnimationController.unbounded(
    vsync: this,
  );

  static const _spring = SpringDescription(
    mass: 1,
    stiffness: 400,
    damping: 18,
  );

  void _to(double target) {
    _hover
        .animateWith(
          SpringSimulation(_spring, _hover.value, target, _hover.velocity),
        )
        // The spring stops within a hair of its target; land exactly on it.
        .whenComplete(() => _hover.value = target);
  }

  @override
  void dispose() {
    _hover.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => _to(1),
      onExit: (_) => _to(0),
      child: AnimatedBuilder(
        animation: _hover,
        builder: (context, _) {
          final v = _hover.value;
          return Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()..translateByDouble(0, -6 * v, 0, 1),
            child: Text(
              widget.text,
              style: widget.style.copyWith(
                color: Color.lerp(
                  widget.style.color,
                  widget.hoverColor,
                  v.clamp(0.0, 1.0),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
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
