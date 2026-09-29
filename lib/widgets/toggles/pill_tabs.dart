// PillTabs — a segmented tab switcher whose pill slides to the selected tab.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Pill Tabs Switcher" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const PillTabs()                                  // Daily / Weekly / Monthly, keeps its own state
//   PillTabs(tabs: ['Day', 'Week'], index: i, onChanged: (v) => setState(() => i = v))
//
// Left/right arrow keys move between tabs when one is focused.

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';

class PillTabs extends StatefulWidget {
  const PillTabs({
    super.key,
    this.tabs = const ['Daily', 'Weekly', 'Monthly'],
    this.index,
    this.onChanged,
    this.initialIndex = 0,
  });

  /// Tab labels, left to right. Must not be empty.
  final List<String> tabs;

  /// The selected tab. Leave null and the switcher keeps its own state.
  final int? index;

  /// Called with the tapped tab's index.
  final ValueChanged<int>? onChanged;

  /// The starting tab when [index] is null.
  final int initialIndex;

  @override
  State<PillTabs> createState() => _PillTabsState();
}

class _PillTabsState extends State<PillTabs> with SingleTickerProviderStateMixin {
  late int _own = widget.initialIndex;
  int? _hovered;

  int get _selected => (widget.index ?? _own).clamp(0, widget.tabs.length - 1);

  // Where the pill is, in tabs (1.5 = halfway between the second and third tab).
  late final AnimationController _pill = AnimationController.unbounded(vsync: this, value: _selected.toDouble());

  static const _spring = SpringDescription(mass: 1, stiffness: 500, damping: 30);
  static const _padding = EdgeInsets.symmetric(horizontal: 14, vertical: 4);

  @override
  void didUpdateWidget(PillTabs oldWidget) {
    super.didUpdateWidget(oldWidget);
    if ((oldWidget.index ?? _own) != _selected) _slide();
  }

  @override
  void dispose() {
    _pill.dispose();
    super.dispose();
  }

  void _select(int i) {
    if (widget.index == null && i != _own) {
      setState(() => _own = i);
      _slide();
    }
    widget.onChanged?.call(i);
  }

  void _slide() {
    final target = _selected.toDouble();
    _pill
        .animateWith(SpringSimulation(_spring, _pill.value, target, _pill.velocity))
        // The spring stops within a hair of its target; land exactly on it.
        .whenComplete(() => _pill.value = target);
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    final step = switch (event.logicalKey) {
      LogicalKeyboardKey.arrowLeft => -1,
      LogicalKeyboardKey.arrowRight => 1,
      _ => 0,
    };
    if (step == 0) return KeyEventResult.ignored;
    final next = (_selected + step).clamp(0, widget.tabs.length - 1);
    if (next != _selected) _select(next);
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final style = DefaultTextStyle.of(context).style.merge(const TextStyle(fontSize: 12, fontWeight: FontWeight.w600));

    // Measure every tab so the pill can stretch between tabs of different widths.
    final scaler = MediaQuery.textScalerOf(context);
    final widths = [
      for (final tab in widget.tabs)
        (TextPainter(
              text: TextSpan(text: tab, style: style),
              textDirection: TextDirection.ltr,
              textScaler: scaler,
            )..layout()).width +
            _padding.horizontal,
    ];
    final lefts = [0.0];
    for (final w in widths) {
      lefts.add(lefts.last + w);
    }

    return Focus(
      onKeyEvent: _onKey,
      skipTraversal: true,
      child: Container(
        padding: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          color: dark ? const Color(0xFF171717) : const Color(0xFFE5E5E5).withValues(alpha: 0.8),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: dark ? Colors.white.withValues(alpha: 0.1) : const Color(0x66D4D4D4)),
        ),
        child: Stack(
          children: [
            // The sliding pill, behind the labels.
            Positioned.fill(
              child: AnimatedBuilder(
                animation: _pill,
                builder: (context, _) {
                  final v = _pill.value.clamp(0.0, widget.tabs.length - 1.0);
                  final i = v.floor().clamp(0, widget.tabs.length - 1);
                  final j = (i + 1).clamp(0, widget.tabs.length - 1);
                  final f = v - i;
                  // Springs can overshoot; let the pill follow a little past the end tabs.
                  final over = _pill.value - v;
                  final left = lefts[i] + (lefts[j] - lefts[i]) * f + over * widths[j];
                  final width = widths[i] + (widths[j] - widths[i]) * f;
                  return Stack(
                    children: [
                      Positioned(
                        left: left,
                        top: 0,
                        bottom: 0,
                        width: width,
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            color: dark ? const Color(0xFF262626) : Colors.white,
                            borderRadius: BorderRadius.circular(999),
                            border: dark ? Border.all(color: Colors.white.withValues(alpha: 0.1)) : null,
                            boxShadow: const [BoxShadow(color: Color(0x0D000000), blurRadius: 2, offset: Offset(0, 1))],
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [for (var i = 0; i < widget.tabs.length; i++) _tab(i, style, dark)],
            ),
          ],
        ),
      ),
    );
  }

  Widget _tab(int i, TextStyle style, bool dark) {
    final selected = i == _selected;
    final Color color;
    if (selected || _hovered == i) {
      color = dark ? Colors.white : Colors.black;
    } else {
      color = dark ? const Color(0xFFA3A3A3) : const Color(0xFF525252);
    }
    return Semantics(
      button: true,
      selected: selected,
      child: FocusableActionDetector(
        mouseCursor: SystemMouseCursors.click,
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _select(i))},
        child: MouseRegion(
          onEnter: (_) => setState(() => _hovered = i),
          onExit: (_) => setState(() => _hovered = null),
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: () => _select(i),
            child: Padding(
              padding: _padding,
              child: AnimatedDefaultTextStyle(
                duration: const Duration(milliseconds: 150),
                style: style.copyWith(color: color),
                child: Text(widget.tabs[i]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
