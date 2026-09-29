// ArcFan — a stack of cards that fans out into an arc.
//
// Copy this file into your project. It depends only on Flutter itself.
//
// Usage:
//   ArcFan(
//     children: [for (final c in colors) Container(width: 120, height: 170, color: c)],
//   )
//
// Hover (desktop/web) or tap (mobile) to fan out. Pass [expanded] to control it yourself.

import 'dart:math' as math;

import 'package:flutter/material.dart';

class ArcFan extends StatefulWidget {
  const ArcFan({
    super.key,
    required this.children,
    this.expanded,
    this.spreadAngle = 70,
    this.radius = 360,
    this.lift = 24,
    this.hoverLift = 28,
    this.duration = const Duration(milliseconds: 650),
    this.stagger = const Duration(milliseconds: 40),
    this.curve = Curves.easeOutBack,
    this.expandOnHover = true,
    this.toggleOnTap = true,
  });

  /// The cards, back to front. Give them all the same size.
  final List<Widget> children;

  /// Controls the fan from outside. When null, hover/tap drive it.
  final bool? expanded;

  /// Total angle of the fan in degrees, from the first card to the last.
  final double spreadAngle;

  /// Distance from the bottom of the cards to the pivot point.
  /// Larger = flatter arc.
  final double radius;

  /// How far the whole fan rises when expanded.
  final double lift;

  /// How far a single hovered card pops up while the fan is open.
  final double hoverLift;

  final Duration duration;

  /// Delay between each card starting to move.
  final Duration stagger;

  final Curve curve;
  final bool expandOnHover;
  final bool toggleOnTap;

  @override
  State<ArcFan> createState() => _ArcFanState();
}

class _ArcFanState extends State<ArcFan> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  bool _open = false;
  int? _hovered;

  int get _count => widget.children.length;
  Duration get _total => widget.duration + widget.stagger * math.max(0, _count - 1);

  @override
  void initState() {
    super.initState();
    _open = widget.expanded ?? false;
    _controller = AnimationController(vsync: this, duration: _total, value: _open ? 1 : 0);
  }

  @override
  void didUpdateWidget(ArcFan oldWidget) {
    super.didUpdateWidget(oldWidget);
    _controller.duration = _total;
    if (widget.expanded != null && widget.expanded != _open) _setOpen(widget.expanded!);
  }

  void _setOpen(bool open) {
    if (open == _open) return;
    setState(() => _open = open);
    open ? _controller.forward() : _controller.reverse();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // Each card gets its own slice of the timeline so they move one after another.
  double _progress(int i) {
    final totalMs = _total.inMicroseconds;
    if (totalMs == 0) return _controller.value;
    final start = (widget.stagger * i).inMicroseconds / totalMs;
    final end = start + widget.duration.inMicroseconds / totalMs;
    final t = Interval(start, end.clamp(0.0, 1.0), curve: widget.curve).transform(_controller.value);
    return t;
  }

  @override
  Widget build(BuildContext context) {
    final controlled = widget.expanded != null;
    final mid = (_count - 1) / 2;
    final step = _count > 1 ? widget.spreadAngle / (_count - 1) : 0.0;

    return MouseRegion(
      onEnter: controlled || !widget.expandOnHover ? null : (_) => _setOpen(true),
      onExit: controlled || !widget.expandOnHover ? null : (_) => _setOpen(false),
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: controlled || !widget.toggleOnTap ? null : () => _setOpen(!_open),
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, _) => Stack(
            clipBehavior: Clip.none,
            alignment: Alignment.bottomCenter,
            children: [
              for (var i = 0; i < _count; i++) _buildCard(i, _progress(i), (i - mid) * step * math.pi / 180),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCard(int i, double t, double angle) {
    return Transform(
      alignment: Alignment.bottomCenter,
      // Pivot sits [radius] below the cards, so rotating traces an arc.
      origin: Offset(0, widget.radius),
      transform: Matrix4.identity()
        ..translateByDouble(0, -widget.lift * t, 0, 1)
        ..rotateZ(angle * t),
      child: MouseRegion(
        onEnter: (_) => setState(() => _hovered = i),
        onExit: (_) => setState(() => _hovered = _hovered == i ? null : _hovered),
        child: TweenAnimationBuilder<double>(
          tween: Tween(end: _open && _hovered == i ? -widget.hoverLift : 0),
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOutCubic,
          builder: (context, dy, child) => Transform.translate(offset: Offset(0, dy), child: child),
          child: widget.children[i],
        ),
      ),
    );
  }
}
