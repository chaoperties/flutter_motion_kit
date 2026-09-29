// CardCoverFlow — a compact 3D cover flow with prev/next controls.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's CardCoverFlow (MIT, (c) 2026 Syed Subhan Uddin).
// (For a larger, draggable cover flow see cover_flow.dart.)
//
// Usage:
//   CardCoverFlow()   // five numbered placeholder cards
//   CardCoverFlow(
//     titles: ['Beach', 'Mountains', 'Forest'],
//     children: [for (final url in photos) Image.network(url, fit: BoxFit.cover)],
//   )
//
// Click a card or a dot, use the arrow buttons, or the left/right keys when focused.

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';

class CardCoverFlow extends StatefulWidget {
  const CardCoverFlow({
    super.key,
    this.children,
    this.titles,
    this.itemCount = 5,
    this.initialIndex = 2,
    this.cardWidth = 80,
    this.onChanged,
  });

  /// The card contents. Defaults to [itemCount] numbered placeholder cards.
  final List<Widget>? children;

  /// Caption shown under the centred card. Defaults to 'Card 1', 'Card 2', ...
  final List<String>? titles;

  /// Number of placeholder cards when [children] is null.
  final int itemCount;
  final int initialIndex;

  /// Width of each card; height is 4/3 of it.
  final double cardWidth;

  final ValueChanged<int>? onChanged;

  @override
  State<CardCoverFlow> createState() => _CardCoverFlowState();
}

class _CardCoverFlowState extends State<CardCoverFlow> with SingleTickerProviderStateMixin {
  late final AnimationController _pos = AnimationController.unbounded(
    vsync: this,
    value: widget.initialIndex.toDouble(),
  );
  late int _index = widget.initialIndex;

  static const _spring = SpringDescription(mass: 1, stiffness: 200, damping: 25);

  int get _count => widget.children?.length ?? widget.itemCount;

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
    final w = widget.cardWidth;
    return Focus(
      onKeyEvent: _onKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: w + 2 * 32 * 2 + 40,
            height: w * 4 / 3 + 40,
            child: AnimatedBuilder(
              animation: _pos,
              builder: (context, _) {
                // Nearest cards paint last, so the centred card is on top.
                final order = [for (var i = 0; i < _count; i++) i]
                  ..sort((a, b) => (b - _pos.value).abs().compareTo((a - _pos.value).abs()));
                return Stack(
                  clipBehavior: Clip.none,
                  alignment: Alignment.topCenter,
                  children: [for (final i in order) _item(i, dark)],
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          _NavPill(count: _count, index: _index, dark: dark, onSelect: _goTo),
        ],
      ),
    );
  }

  Widget _item(int i, bool dark) {
    final d = i - _pos.value;
    final a = d.abs();
    final near = a.clamp(0.0, 1.0);
    // Centre card pops forward (z 50, scale 1.1); others step back and turn 38° away.
    final z = a < 1 ? 50 - 100 * a : -50 * a;
    final scale = a < 1 ? 1.1 + (0.92 - 1.1) * a : 1 - 0.08 * a;
    final opacity = a <= 2 ? 1 - 0.25 * a : (0.5 * (3 - a)).clamp(0.0, 1.0);
    final title = widget.titles != null && i < widget.titles!.length ? widget.titles![i] : 'Card ${i + 1}';
    final w = widget.cardWidth;

    return Positioned(
      key: ValueKey(i),
      top: 10,
      child: Opacity(
        opacity: opacity,
        child: Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()
            // Same perspective as CSS `perspective: 1000px` (z points at the viewer).
            ..setEntry(3, 2, -1 / 1000)
            ..translateByDouble(d * 32, 0, z, 1)
            ..rotateY(-d.clamp(-1.0, 1.0) * 38 * math.pi / 180)
            ..scaleByDouble(scale, scale, 1, 1),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              GestureDetector(
                onTap: () => _goTo(i),
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: Container(
                    width: w,
                    height: w * 4 / 3,
                    decoration: BoxDecoration(
                      color: dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0x33E5E5E5)),
                      boxShadow: const [
                        BoxShadow(
                          color: Color(0x40000000),
                          blurRadius: 25,
                          offset: Offset(0, 12),
                          spreadRadius: -6,
                        ),
                      ],
                    ),
                    clipBehavior: Clip.antiAlias,
                    alignment: Alignment.center,
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
                ),
              ),
              const SizedBox(height: 6),
              Transform.translate(
                offset: Offset(0, -5 * near),
                child: Opacity(
                  opacity: 1 - near,
                  child: SizedBox(
                    width: w + 40,
                    child: Text(
                      title,
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: (dark ? Colors.white : Colors.black).withValues(alpha: 0.8),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
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
            child: Icon(icon, size: 14, color: ink.withValues(alpha: 0.7)),
          ),
        ),
      ),
    );

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: ink.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: ink.withValues(alpha: 0.1)),
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
