// SpringText — characters spring up and light up under the pointer.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Spring Text" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const SpringText('AMICRO UI')
//   SpringText('Hello world', style: TextStyle(fontSize: 48))
//
// Reacts to a mouse pointer; on touch screens the text simply stays still.

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class SpringText extends StatelessWidget {
  const SpringText(
    this.text, {
    super.key,
    this.style,
    this.color,
    this.hoverColor = const Color(0xFF6366F1),
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
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: dark ? Colors.white : Colors.black,
          ),
        )
        .merge(this.style);
    if (color != null) style = style.copyWith(color: color);
    return Semantics(
      label: text,
      child: ExcludeSemantics(
        child: _splitChars(
          text,
          (unit, _) =>
              _HoverUnit(text: unit, style: style, hoverColor: hoverColor),
        ),
      ),
    );
  }
}

/// One character that springs towards its hover pose.
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
    stiffness: 500,
    damping: 15,
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
              ..translateByDouble(0, -8 * v, 0, 1)
              ..scaleByDouble(1 + 0.2 * v, 1 + 0.2 * v, 1, 1),
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
