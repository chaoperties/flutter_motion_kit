// CardCarousel — a row of cards that tilts into an arc when hovered.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's CardCarousel (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   CardCarousel()   // five numbered placeholder cards
//   CardCarousel(
//     titles: ['Beach', 'Mountains', 'Forest'],
//     children: [for (final url in photos) Image.network(url, fit: BoxFit.cover)],
//   )
//
// Click a card or a dot, use the arrow buttons, or the left/right keys when focused.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';

class CardCarousel extends StatefulWidget {
  const CardCarousel({
    super.key,
    this.children,
    this.titles,
    this.itemCount = 5,
    this.initialIndex = 2,
    this.hovered,
    this.cardSize = 110,
    this.slideWidth = 160,
    this.onChanged,
  });

  /// The card contents. Defaults to [itemCount] numbered placeholder cards.
  final List<Widget>? children;

  /// Caption shown above the centred card. Defaults to 'Card 1', 'Card 2', ...
  final List<String>? titles;

  /// Number of placeholder cards when [children] is null.
  final int itemCount;
  final int initialIndex;

  /// Tilts the row into an arc. When null, hovering the carousel does it.
  final bool? hovered;

  /// Width and height of each (square) card.
  final double cardSize;

  /// Distance between card centres.
  final double slideWidth;

  final ValueChanged<int>? onChanged;

  @override
  State<CardCarousel> createState() => _CardCarouselState();
}

class _CardCarouselState extends State<CardCarousel> with TickerProviderStateMixin {
  // Scroll position in cards (2.0 = card 2 centred) and hover amount (0..1), both spring-driven.
  late final AnimationController _pos = AnimationController.unbounded(
    vsync: this,
    value: widget.initialIndex.toDouble(),
  );
  late final AnimationController _tilt = AnimationController.unbounded(
    vsync: this,
    value: (widget.hovered ?? false) ? 1 : 0,
  );
  late int _index = widget.initialIndex;
  bool _hover = false;

  static final _slideSpring = SpringDescription.withDampingRatio(mass: 1, stiffness: 90, ratio: 0.9);
  static final _tiltSpring = SpringDescription.withDampingRatio(mass: 1, stiffness: 90, ratio: 0.8);

  int get _count => widget.children?.length ?? widget.itemCount;

  @override
  void didUpdateWidget(CardCarousel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.hovered != widget.hovered) _animateTilt();
  }

  @override
  void dispose() {
    _pos.dispose();
    _tilt.dispose();
    super.dispose();
  }

  void _goTo(int index) {
    final next = index.clamp(0, _count - 1);
    if (next != _index) {
      setState(() => _index = next);
      widget.onChanged?.call(next);
    }
    _pos.animateWith(SpringSimulation(_slideSpring, _pos.value, next.toDouble(), _pos.velocity));
  }

  void _setHover(bool value) {
    if (widget.hovered != null || value == _hover) return;
    _hover = value;
    _animateTilt();
  }

  void _animateTilt() {
    final target = (widget.hovered ?? _hover) ? 1.0 : 0.0;
    _tilt.animateWith(SpringSimulation(_tiltSpring, _tilt.value, target, _tilt.velocity));
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
      _goTo(_index - 1);
    } else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
      _goTo(_index + 1);
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Focus(
      onKeyEvent: _onKey,
      child: MouseRegion(
        onEnter: (_) => _setHover(true),
        onExit: (_) => _setHover(false),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              height: 180,
              child: AnimatedBuilder(
                animation: Listenable.merge([_pos, _tilt]),
                builder: (context, _) => LayoutBuilder(
                  builder: (context, box) {
                    final width = box.hasBoundedWidth ? box.maxWidth : widget.slideWidth * 3;
                    // Clip sideways only (like Amicro's overflow-hidden) so tilted cards keep their tops.
                    return ClipRect(
                      clipper: const _HorizontalClip(),
                      child: SizedBox(
                        width: width,
                        child: Stack(
                          clipBehavior: Clip.none,
                          alignment: Alignment.center,
                          children: [for (var i = 0; i < _count; i++) _slide(i, dark)],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
            const SizedBox(height: 16),
            _NavPill(count: _count, index: _index, dark: dark, onSelect: _goTo),
          ],
        ),
      ),
    );
  }

  Widget _slide(int i, bool dark) {
    final diff = i - _pos.value;
    final h = _tilt.value;
    final near = diff.abs().clamp(0.0, 1.0);
    final sideScale = 0.8 + (0.65 - 0.8) * h;
    final title = widget.titles != null && i < widget.titles!.length ? widget.titles![i] : 'Card ${i + 1}';

    return Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()
        ..translateByDouble(diff * widget.slideWidth, diff * 24 * h, 0, 1)
        ..rotateZ(diff * (5 + 15 * h) * math.pi / 180)
        ..scaleByDouble(1.05 + (sideScale - 1.05) * near, 1.05 + (sideScale - 1.05) * near, 1, 1),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Opacity(
            opacity: 1 - near,
            child: Transform.scale(
              scale: 1 - 0.25 * near,
              child: Text(
                title,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: dark ? Colors.white : const Color(0xFF171717),
                ),
              ),
            ),
          ),
          const SizedBox(height: 6),
          GestureDetector(
            onTap: () => _goTo(i),
            child: MouseRegion(cursor: SystemMouseCursors.click, child: _card(i, dark)),
          ),
        ],
      ),
    );
  }

  Widget _card(int i, bool dark) {
    final child = widget.children?[i];
    return Container(
      width: widget.cardSize,
      height: widget.cardSize,
      decoration: BoxDecoration(
        color: dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x33E5E5E5)),
        boxShadow: const [
          BoxShadow(color: Color(0x33000000), blurRadius: 15, offset: Offset(0, 10), spreadRadius: -3),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      alignment: Alignment.center,
      child:
          child ??
          Text(
            '${i + 1}',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: dark ? const Color(0xFFA3A3A3) : const Color(0xFF525252),
            ),
          ),
    );
  }
}

/// Prev / dots / next controls in a small frosted pill.
class _NavPill extends StatelessWidget {
  const _NavPill({required this.count, required this.index, required this.dark, required this.onSelect});

  final int count;
  final int index;
  final bool dark;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    final ink = dark ? Colors.white : Colors.black;
    Widget arrow(IconData icon, int to, String label) => Semantics(
      button: true,
      label: label,
      child: GestureDetector(
        onTap: () => onSelect(to),
        child: MouseRegion(
          cursor: SystemMouseCursors.click,
          child: Padding(
            padding: const EdgeInsets.all(4),
            child: Icon(icon, size: 14, color: ink.withValues(alpha: 0.6)),
          ),
        ),
      ),
    );

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: ink.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: ink.withValues(alpha: 0.08)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          arrow(Icons.chevron_left_rounded, index - 1, 'Previous'),
          const SizedBox(width: 4),
          for (var i = 0; i < count; i++)
            GestureDetector(
              onTap: () => onSelect(i),
              child: MouseRegion(
                cursor: SystemMouseCursors.click,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeOutCubic,
                  margin: const EdgeInsets.symmetric(horizontal: 2, vertical: 6),
                  width: i == index ? 16 : 4,
                  height: 4,
                  decoration: BoxDecoration(
                    color: ink.withValues(alpha: i == index ? 1 : 0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
            ),
          const SizedBox(width: 4),
          arrow(Icons.chevron_right_rounded, index + 1, 'Next'),
        ],
      ),
    );
  }
}

class _HorizontalClip extends CustomClipper<Rect> {
  const _HorizontalClip();

  @override
  Rect getClip(Size size) => Rect.fromLTRB(0, -size.height, size.width, size.height * 2);

  @override
  bool shouldReclip(_HorizontalClip oldClipper) => false;
}
