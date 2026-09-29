// CoverFlow — a 3D carousel: the centre item faces you, neighbours turn away.
//
// Copy this file into your project. It depends only on Flutter itself.
//
// Usage:
//   CoverFlow(
//     itemCount: covers.length,
//     itemBuilder: (context, i) => Image.network(covers[i], fit: BoxFit.cover),
//     onChanged: (i) => print('now showing $i'),
//   )
//
// Drag or swipe to scroll, tap a side item to bring it to the centre,
// or use the left/right arrow keys when it has focus.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';

class CoverFlow extends StatefulWidget {
  const CoverFlow({
    super.key,
    required this.itemCount,
    required this.itemBuilder,
    this.initialIndex = 0,
    this.itemSize = const Size(180, 240),
    this.spacing = 120,
    this.sideSpacing = 48,
    this.rotation = 55,
    this.sideScale = 0.82,
    this.perspective = 0.0015,
    this.visibleSideItems = 3,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.onChanged,
  });

  final int itemCount;
  final IndexedWidgetBuilder itemBuilder;
  final int initialIndex;

  /// Size of every item.
  final Size itemSize;

  /// Distance from the centre item to its direct neighbours.
  final double spacing;

  /// Distance between items further out (they bunch up, like a shelf).
  final double sideSpacing;

  /// How far side items turn away, in degrees.
  final double rotation;

  /// Scale of side items relative to the centre item.
  final double sideScale;

  /// Strength of the 3D effect. 0 = flat.
  final double perspective;

  /// How many items to draw on each side of the centre.
  final int visibleSideItems;

  final BorderRadius borderRadius;

  /// Called when the centred item changes.
  final ValueChanged<int>? onChanged;

  @override
  State<CoverFlow> createState() => _CoverFlowState();
}

class _CoverFlowState extends State<CoverFlow> with SingleTickerProviderStateMixin {
  // The controller's value is the scroll position in "items": 2.5 = halfway between item 2 and 3.
  late final AnimationController _position = AnimationController.unbounded(
    vsync: this,
    value: widget.initialIndex.toDouble(),
  )..addListener(_notifyIfChanged);
  late int _current = widget.initialIndex;

  static const _spring = SpringDescription(mass: 1, stiffness: 180, damping: 22);

  int get _last => math.max(0, widget.itemCount - 1);

  @override
  void dispose() {
    _position.dispose();
    super.dispose();
  }

  void _notifyIfChanged() {
    final index = _position.value.round().clamp(0, _last);
    if (index != _current) {
      _current = index;
      widget.onChanged?.call(index);
    }
  }

  void _animateTo(double target, {double velocity = 0}) {
    final sim = SpringSimulation(_spring, _position.value, target.clamp(0, _last.toDouble()), velocity);
    _position.animateWith(sim);
  }

  void _onDragUpdate(DragUpdateDetails d) {
    var next = _position.value - d.delta.dx / widget.spacing;
    // Rubber-band past the ends.
    if (next < 0 || next > _last) next = _position.value - d.delta.dx / widget.spacing / 3;
    _position.value = next;
  }

  void _onDragEnd(DragEndDetails d) {
    final velocity = -d.velocity.pixelsPerSecond.dx / widget.spacing;
    // Project where a flick would land, then snap to the nearest item.
    final target = (_position.value + velocity * 0.18).roundToDouble();
    _animateTo(target, velocity: velocity);
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
      _animateTo(_current - 1);
    } else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
      _animateTo(_current + 1);
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  // Horizontal offset for an item [d] items away from centre.
  double _xFor(double d) {
    final a = d.abs();
    final x = a <= 1 ? a * widget.spacing : widget.spacing + (a - 1) * widget.sideSpacing;
    return x * d.sign;
  }

  @override
  Widget build(BuildContext context) {
    final height = widget.itemSize.height * 1.15;
    // Side items sit outside the centre item's box, so the carousel must be wide
    // enough to contain them or they can't be tapped or dragged.
    final naturalWidth = widget.itemSize.width + 2 * _xFor(widget.visibleSideItems.toDouble());
    return Focus(
      onKeyEvent: _onKey,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onHorizontalDragStart: (_) => _position.stop(),
        onHorizontalDragUpdate: _onDragUpdate,
        onHorizontalDragEnd: _onDragEnd,
        child: LayoutBuilder(
          builder: (context, constraints) => SizedBox(
            width: constraints.hasBoundedWidth ? constraints.maxWidth : naturalWidth,
            height: height,
            child: AnimatedBuilder(
              animation: _position,
              builder: (context, _) {
                final pos = _position.value;
                final first = math.max(0, (pos - widget.visibleSideItems).floor());
                final last = math.min(_last, (pos + widget.visibleSideItems).ceil());
                // Paint far items first so the centre item ends up on top.
                final indices = [for (var i = first; i <= last; i++) i]
                  ..sort((a, b) => (b - pos).abs().compareTo((a - pos).abs()));
                return Stack(
                  clipBehavior: Clip.none,
                  alignment: Alignment.center,
                  children: [for (final i in indices) _buildItem(context, i, i - pos)],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildItem(BuildContext context, int index, double d) {
    final turn = d.clamp(-1.0, 1.0);
    final scale = 1 - (1 - widget.sideScale) * turn.abs();
    final fade = (1 - (d.abs() - widget.visibleSideItems + 1)).clamp(0.0, 1.0);

    return Transform(
      key: ValueKey(index),
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..setEntry(3, 2, widget.perspective)
        ..translateByDouble(_xFor(d), 0, 0, 1)
        ..rotateY(-turn * widget.rotation * math.pi / 180)
        ..scaleByDouble(scale, scale, 1, 1),
      child: Opacity(
        opacity: fade,
        child: GestureDetector(
          onTap: () => _animateTo(index.toDouble()),
          child: SizedBox.fromSize(
            size: widget.itemSize,
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: widget.borderRadius,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.25 * (1 - turn.abs() * 0.5)),
                    blurRadius: 24,
                    offset: const Offset(0, 12),
                  ),
                ],
              ),
              child: ClipRRect(borderRadius: widget.borderRadius, child: widget.itemBuilder(context, index)),
            ),
          ),
        ),
      ),
    );
  }
}
