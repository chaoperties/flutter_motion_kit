// CardLinearSpread — a stack that slides apart into a straight row.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's CardLinearSpread (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   CardLinearSpread()
//
// Hover (desktop/web) or tap (touch) to spread; pass `hovered` to drive it yourself.

import 'dart:math' as math;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class CardLinearSpread extends StatefulWidget {
  const CardLinearSpread({
    super.key,
    this.children,
    this.hovered,
    this.cardSize = const Size(128, 176),
    this.intensity = 1,
    this.gap = 90,
  });

  /// The cards, back to front. Defaults to plain neutral cards.
  final List<Widget>? children;

  /// Drives the layout from outside. When null, hover (or tap on touch screens) drives it.
  final bool? hovered;

  /// Size of every card.
  final Size cardSize;

  /// Multiplies how far the cards travel and turn. 0 keeps them stacked.
  final double intensity;

  /// Horizontal distance of the outermost cards from the centre.
  final double gap;

  @override
  State<CardLinearSpread> createState() => _CardLinearSpreadState();
}

class _CardLinearSpreadState extends State<CardLinearSpread> with SingleTickerProviderStateMixin {
  // 0 = resting pile, 1 = spread. A spring drives it, so reversing mid-flight keeps momentum.
  late final AnimationController _t = AnimationController.unbounded(
    vsync: this,
    value: (widget.hovered ?? false) ? 1 : 0,
  );
  bool _hover = false;

  static const _spring = SpringDescription(mass: 0.8, stiffness: 180, damping: 20);

  bool get _active => widget.hovered ?? _hover;
  int get _count => 5;

  @override
  void didUpdateWidget(CardLinearSpread oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.hovered != widget.hovered) _animate();
  }

  @override
  void dispose() {
    _t.dispose();
    super.dispose();
  }

  void _setHover(bool value) {
    if (widget.hovered != null || value == _hover) return;
    setState(() => _hover = value);
    _animate();
  }

  void _animate() => _t.animateWith(SpringSimulation(_spring, _t.value, _active ? 1 : 0, _t.velocity));

  _Pose _rest(int i, double dist) {
    return const _Pose();
  }

  _Pose _spread(int i, double dist) {
    final k = widget.intensity;
    return _Pose(x: dist * (widget.gap / 2) * k, scale: dist == 0 ? 1.05 : 1);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final children = widget.children;
    assert(children == null || children.length == _count, 'CardLinearSpread needs exactly $_count children.');
    final centre = (_count - 1) / 2;
    // Paint the cards furthest back first, so the front card ends up on top.
    final order = [for (var i = 0; i < _count; i++) i]
      ..sort((a, b) {
        double z(int i) {
          final dist = i - centre;
          return -dist.abs();
        }

        return z(a).compareTo(z(b));
      });

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => _setHover(true),
      onExit: (_) => _setHover(false),
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        // Touch has no hover, so a tap toggles instead. (A mouse click would fight the hover.)
        onTapUp: (d) {
          if (d.kind == PointerDeviceKind.touch) _setHover(!_hover);
        },
        child: SizedBox.fromSize(
          size: widget.cardSize,
          child: AnimatedBuilder(
            animation: _t,
            builder: (context, _) => Stack(
              clipBehavior: Clip.none,
              children: [
                for (final i in order)
                  Positioned.fill(key: ValueKey(i), child: _card(i, i - centre, dark, children?[i])),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _card(int i, double dist, bool dark, Widget? child) {
    final p = _Pose.lerp(_rest(i, dist), _spread(i, dist), _t.value);
    return Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..translateByDouble(p.x, p.y, 0, 1)
        ..rotateZ(p.rotate * math.pi / 180)
        ..scaleByDouble(p.scale, p.scale, 1, 1),
      child: _shell(dark, child),
    );
  }
}

/// Where a card sits: offset in pixels, rotation in degrees, and scale.
class _Pose {
  const _Pose({this.x = 0, this.y = 0, this.rotate = 0, this.scale = 1});

  final double x, y, rotate, scale;

  static _Pose lerp(_Pose a, _Pose b, double t) => _Pose(
    x: a.x + (b.x - a.x) * t,
    y: a.y + (b.y - a.y) * t,
    rotate: a.rotate + (b.rotate - a.rotate) * t,
    scale: a.scale + (b.scale - a.scale) * t,
  );
}

Widget _shell(bool dark, Widget? child) => DecoratedBox(
  decoration: BoxDecoration(
    color: dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3),
    borderRadius: BorderRadius.circular(16),
    border: Border.all(color: const Color(0x33E5E5E5)),
    boxShadow: const [
      BoxShadow(color: Color(0x26000000), blurRadius: 10, spreadRadius: -2, offset: Offset(0, 4)),
      BoxShadow(color: Color(0x1A000000), blurRadius: 6, spreadRadius: -2, offset: Offset(0, 2)),
    ],
  ),
  child: ClipRRect(borderRadius: BorderRadius.circular(15), child: child ?? const SizedBox.expand()),
);
