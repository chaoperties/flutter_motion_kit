// LinearSpread — a messy stack of cards that slides out into a neat row.
//
// Copy this file into your project. It depends only on Flutter itself.
//
// Usage:
//   LinearSpread(
//     children: [for (final c in colors) Container(width: 100, height: 140, color: c)],
//   )
//
// Hover (desktop/web) or tap (mobile) to spread. Pass [expanded] to control it yourself.

import 'dart:math' as math;

import 'package:flutter/material.dart';

class LinearSpread extends StatefulWidget {
  const LinearSpread({
    super.key,
    required this.children,
    this.expanded,
    this.spacing = 116,
    this.stackTilt = 4,
    this.stackOffset = 3,
    this.duration = const Duration(milliseconds: 600),
    this.stagger = const Duration(milliseconds: 35),
    this.curve = Curves.easeOutCubic,
    this.expandOnHover = true,
    this.toggleOnTap = true,
  });

  /// The cards, back to front. Give them all the same size.
  final List<Widget> children;

  /// Controls the spread from outside. When null, hover/tap drive it.
  final bool? expanded;

  /// Horizontal distance between card centres when spread.
  final double spacing;

  /// Rotation in degrees applied alternately to cards while stacked.
  final double stackTilt;

  /// Pixel offset between cards while stacked.
  final double stackOffset;

  final Duration duration;

  /// Delay between each card starting to move (fans out from the centre).
  final Duration stagger;

  final Curve curve;
  final bool expandOnHover;
  final bool toggleOnTap;

  @override
  State<LinearSpread> createState() => _LinearSpreadState();
}

class _LinearSpreadState extends State<LinearSpread> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  bool _open = false;

  int get _count => widget.children.length;
  double get _mid => (_count - 1) / 2;
  int get _maxRank => _mid.ceil();
  Duration get _total => widget.duration + widget.stagger * _maxRank;

  @override
  void initState() {
    super.initState();
    _open = widget.expanded ?? false;
    _controller = AnimationController(vsync: this, duration: _total, value: _open ? 1 : 0);
  }

  @override
  void didUpdateWidget(LinearSpread oldWidget) {
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

  // Cards nearest the centre move first, outer cards follow.
  double _progress(int i) {
    final totalUs = _total.inMicroseconds;
    if (totalUs == 0) return _controller.value;
    final rank = (i - _mid).abs().floor();
    final start = (widget.stagger * rank).inMicroseconds / totalUs;
    final end = start + widget.duration.inMicroseconds / totalUs;
    return Interval(start, end.clamp(0.0, 1.0), curve: widget.curve).transform(_controller.value);
  }

  @override
  Widget build(BuildContext context) {
    final controlled = widget.expanded != null;

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
            alignment: Alignment.center,
            children: [for (var i = 0; i < _count; i++) _buildCard(i, _progress(i))],
          ),
        ),
      ),
    );
  }

  Widget _buildCard(int i, double t) {
    final fromCentre = i - _mid;
    // Stacked pose: small alternating tilt and offset so it looks like a real pile.
    final tilt = (i.isEven ? 1 : -1) * widget.stackTilt * math.pi / 180;
    final stacked = Offset(fromCentre * widget.stackOffset, -i * widget.stackOffset * 0.5);
    final spread = Offset(fromCentre * widget.spacing, 0);
    final offset = Offset.lerp(stacked, spread, t)!;

    return Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..translateByDouble(offset.dx, offset.dy, 0, 1)
        ..rotateZ(tilt * (1 - t)),
      child: widget.children[i],
    );
  }
}
