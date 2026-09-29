// HoverScaleChar — characters grow under the pointer.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Hover Scale Char" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const HoverScaleChar('AMICRO UI')
//   HoverScaleChar('Hello world', style: TextStyle(fontSize: 48))
//
// Reacts to a mouse pointer; on touch screens the text simply stays still.

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class HoverScaleChar extends StatelessWidget {
  const HoverScaleChar(this.text, {super.key, this.style, this.color});

  final String text;

  /// Merged over the default style.
  final TextStyle? style;

  /// Defaults to pink for the current light/dark theme.
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    var style = DefaultTextStyle.of(context).style
        .merge(
          TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: dark ? const Color(0xFFF472B6) : const Color(0xFFDB2777),
          ),
        )
        .merge(this.style);
    if (color != null) style = style.copyWith(color: color);
    return Semantics(
      label: text,
      child: ExcludeSemantics(
        child: _splitChars(
          text,
          (unit, _) => _HoverUnit(text: unit, style: style),
        ),
      ),
    );
  }
}

/// One character that springs towards its hover pose.
class _HoverUnit extends StatefulWidget {
  const _HoverUnit({required this.text, required this.style});

  final String text;
  final TextStyle style;

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
    stiffness: 500,
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
            transform: Matrix4.identity()
              ..scaleByDouble(1 + 0.4 * v, 1 + 0.4 * v, 1, 1),
            child: Text(widget.text, style: widget.style),
          );
        },
      ),
    );
  }
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
