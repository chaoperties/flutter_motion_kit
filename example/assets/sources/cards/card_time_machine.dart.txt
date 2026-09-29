// CardTimeMachine — an Apple Time Machine–style stack with a timeline scrubber.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's CardTimeMachine (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   CardTimeMachine()   // five numbered placeholder cards
//   CardTimeMachine(
//     labels: ['Today', 'Yesterday', 'Last week'],
//     children: [for (final url in snapshots) Image.network(url, fit: BoxFit.cover)],
//   )
//
// Hover (or tap) the timeline on the right to travel back; up/down keys work when focused.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';

class CardTimeMachine extends StatefulWidget {
  const CardTimeMachine({
    super.key,
    this.children,
    this.labels = const ['Today', '1d ago', '1w ago', '1m ago', '1y ago'],
    this.initialIndex = 0,
    this.cardSize = const Size(220, 135),
    this.accent = const Color(0xFF3B82F6),
    this.framed = true,
    this.onChanged,
  });

  /// One card per label, newest first. Defaults to numbered placeholder cards.
  final List<Widget>? children;

  /// Timeline labels, newest first. Its length sets the number of cards.
  final List<String> labels;

  final int initialIndex;
  final Size cardSize;

  /// Colour of the selected timeline tick.
  final Color accent;

  /// Draws the dark rounded panel behind everything, as in Amicro.
  final bool framed;

  final ValueChanged<int>? onChanged;

  @override
  State<CardTimeMachine> createState() => _CardTimeMachineState();
}

class _CardTimeMachineState extends State<CardTimeMachine> with SingleTickerProviderStateMixin {
  // How far back in time we are, in cards (1.0 = the second card is in front).
  late final AnimationController _pos = AnimationController.unbounded(
    vsync: this,
    value: widget.initialIndex.toDouble(),
  );
  late int _index = widget.initialIndex;
  double? _hovered; // timeline position under the pointer; sub-ticks are fractional

  static const _spring = SpringDescription(mass: 0.8, stiffness: 250, damping: 25);

  int get _count => widget.labels.length;

  @override
  void dispose() {
    _pos.dispose();
    super.dispose();
  }

  void _goTo(int index) {
    final next = index.clamp(0, _count - 1);
    if (next != _index) {
      setState(() => _index = next);
      widget.onChanged?.call(next);
    }
    _pos.animateWith(SpringSimulation(_spring, _pos.value, next.toDouble(), _pos.velocity));
  }

  void _scrub(double at) {
    setState(() => _hovered = at);
    _goTo(at.round());
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
      _goTo(_index + 1);
    } else if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
      _goTo(_index - 1);
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) {
    // The frame is always dark, so inside it we style for dark regardless of the app theme.
    final dark = widget.framed || Theme.of(context).brightness == Brightness.dark;
    final content = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: widget.cardSize.width + 70,
          height: widget.cardSize.height + 80,
          child: AnimatedBuilder(
            animation: _pos,
            builder: (context, _) => Stack(
              clipBehavior: Clip.none,
              alignment: Alignment.center,
              // Oldest at the back: paint from the last card to the first.
              children: [for (var i = _count - 1; i >= 0; i--) _card(i, dark)],
            ),
          ),
        ),
        const SizedBox(width: 24),
        _timeline(dark),
      ],
    );

    return Focus(
      onKeyEvent: _onKey,
      child: widget.framed
          ? Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xCC09090B),
                gradient: const RadialGradient(colors: [Color(0x08FFFFFF), Color(0x00FFFFFF)], radius: 0.7),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0x0DFFFFFF)),
              ),
              child: content,
            )
          : content,
    );
  }

  Widget _card(int i, bool dark) {
    final o = i - _pos.value;
    // Cards ahead of us stack into the distance. A card we've gone past flies up
    // towards the viewer and fades out; between 0 and -1 it blends into that pose.
    double z, y, rotX, opacity, scale;
    if (o >= 0) {
      z = -o * 60;
      y = -o * 12;
      rotX = o * 2;
      opacity = 1 - o * 0.2;
      scale = 1;
    } else {
      final p = math.min(-o, 1.0);
      z = 200 * p;
      y = 300 * p;
      rotX = -20 * p;
      opacity = 1 - p;
      scale = 1 + 0.3 * p;
    }
    if (opacity <= 0.01) return const SizedBox.shrink();

    return IgnorePointer(
      child: Opacity(
        opacity: opacity.clamp(0.0, 1.0),
        child: Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()
            // Same perspective as CSS `perspective: 800px` (z points at the viewer).
            ..setEntry(3, 2, -1 / 800)
            ..translateByDouble(0, y, z, 1)
            ..rotateX(rotX * math.pi / 180)
            ..scaleByDouble(scale, scale, 1, 1),
          child: Container(
            width: widget.cardSize.width,
            height: widget.cardSize.height,
            decoration: BoxDecoration(
              color: dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0x33E5E5E5)),
              boxShadow: const [BoxShadow(color: Color(0x40000000), blurRadius: 15, offset: Offset(0, 10))],
            ),
            clipBehavior: Clip.antiAlias,
            alignment: Alignment.center,
            child: Stack(
              fit: StackFit.expand,
              children: [
                Center(
                  child:
                      widget.children?[i] ??
                      Text(
                        '${i + 1}',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: dark ? const Color(0xFFA3A3A3) : const Color(0xFF525252),
                        ),
                      ),
                ),
                const ColoredBox(color: Color(0x1A000000)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _timeline(bool dark) {
    // Each label gets a main tick; two faint sub-ticks sit between neighbours.
    final nodes = <(bool main, double at)>[
      for (var i = 0; i < _count; i++) ...[
        (true, i.toDouble()),
        if (i < _count - 1) ...[(false, i + 0.33), (false, i + 0.66)],
      ],
    ];

    final ink = dark ? Colors.white : Colors.black;
    return MouseRegion(
      onExit: (_) => setState(() => _hovered = null),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [for (final (main, at) in nodes) main ? _mainTick(at.round(), ink) : _subTick(at, ink)],
      ),
    );
  }

  Widget _mainTick(int i, Color ink) {
    final selected = _index == i;
    final hovered = _hovered;
    final scaleX = hovered == null ? 1.0 : (selected ? 1.4 : ((i - hovered).abs() < 0.5 ? 1.25 : 1.0));
    return _Hit(
      onEnter: () => _scrub(i.toDouble()),
      onTap: () => _goTo(i),
      label: widget.labels[i],
      child: SizedBox(
        width: 80,
        height: 5,
        child: Stack(
          clipBehavior: Clip.none,
          alignment: Alignment.centerRight,
          children: [
            if (hovered == i)
              Positioned(
                right: 40,
                top: -5,
                child: TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0, end: 1),
                  duration: const Duration(milliseconds: 150),
                  builder: (context, t, child) => Opacity(
                    opacity: t,
                    child: Transform.scale(scale: 0.8 + 0.2 * t, child: child),
                  ),
                  child: Text(
                    widget.labels[i],
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: selected ? widget.accent : ink.withValues(alpha: 0.9),
                    ),
                  ),
                ),
              ),
            _Tick(scaleX: scaleX, color: selected ? widget.accent : ink.withValues(alpha: 0.5)),
          ],
        ),
      ),
    );
  }

  Widget _subTick(double at, Color ink) {
    final near = _hovered != null && (at - _hovered!).abs() <= 0.5;
    return _Hit(
      onEnter: () => _scrub(at),
      onTap: () => _goTo(at.round()),
      child: SizedBox(
        width: 80,
        height: 5,
        child: Align(
          alignment: Alignment.centerRight,
          child: _Tick(
            scaleX: near ? 1.15 : 1,
            color: ink.withValues(alpha: 0.2 * (near ? 0.5 : 0.3)),
          ),
        ),
      ),
    );
  }
}

/// A hover/tap target for one timeline row.
class _Hit extends StatelessWidget {
  const _Hit({required this.onEnter, required this.onTap, required this.child, this.label});

  final VoidCallback onEnter;
  final VoidCallback onTap;
  final Widget child;
  final String? label;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: label != null,
      label: label,
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        onEnter: (_) => onEnter(),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: onTap,
          child: Padding(padding: const EdgeInsets.symmetric(vertical: 1), child: child),
        ),
      ),
    );
  }
}

/// A 24x3 timeline tick that stretches leftwards from its right edge.
class _Tick extends StatelessWidget {
  const _Tick({required this.scaleX, required this.color});

  final double scaleX;
  final Color color;

  static final _spring = SpringSimulation(
    const SpringDescription(mass: 1, stiffness: 400, damping: 25),
    0,
    1,
    0,
  );

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(end: scaleX),
      duration: const Duration(milliseconds: 370),
      curve: const _SpringCurve(),
      builder: (context, sx, _) => Transform(
        alignment: Alignment.centerRight,
        transform: Matrix4.diagonal3Values(sx, 1, 1),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: 24,
          height: 3,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
        ),
      ),
    );
  }
}

/// Spring (stiffness 400, damping 25) as a curve over 370ms.
class _SpringCurve extends Curve {
  const _SpringCurve();

  @override
  double transformInternal(double t) => _Tick._spring.x(t * 0.37);
}
