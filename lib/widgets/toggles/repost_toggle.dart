// RepostToggle — a repost button whose arrows turn half a circle.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Repost Action" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   RepostToggle(count: 18)                              // shows 18, or 19 when on
//   RepostToggle(count: post.count, value: post.mine, onChanged: toggle)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class RepostToggle extends StatefulWidget {
  const RepostToggle({
    super.key,
    this.value,
    this.onChanged,
    this.initialValue = false,
    this.count = 0,
    this.semanticLabel,
  });

  /// Whether the button is on. Leave null and the button keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  /// The count without this user's vote; one is added while the button is on.
  final int count;

  /// What a screen reader announces before the count, e.g. "Repost".
  final String? semanticLabel;

  @override
  State<RepostToggle> createState() => _RepostToggleState();
}

class _RepostToggleState extends State<RepostToggle> with SingleTickerProviderStateMixin {
  late bool _own = widget.initialValue;
  bool _hovered = false;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Rotation of the arrows: 0 = off, 1 = half a turn.
  late final AnimationController _icon = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 300),
    value: _on ? 1 : 0,
  );

  @override
  void didUpdateWidget(RepostToggle oldWidget) {
    super.didUpdateWidget(oldWidget);
    final was = oldWidget.value ?? _own;
    if (was != _on) _react();
  }

  @override
  void dispose() {
    _icon.dispose();
    super.dispose();
  }

  void _toggle() {
    final next = !_on;
    if (widget.value == null) {
      setState(() => _own = next);
      _react();
    }
    widget.onChanged?.call(next);
  }

  void _react() {
    if (_on) {
      _icon.animateTo(1, curve: Curves.easeInOut);
    } else {
      _icon.animateBack(0, curve: Curves.easeInOut);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final bg = on
        ? const Color(0xFF10B981).withValues(alpha: 0.2)
        : dark
        ? Colors.white.withValues(alpha: 0.05)
        : const Color(0xFFF5F5F5);
    final fg = on
        ? const Color(0xFF34D399)
        : dark
        ? (_hovered ? Colors.white : const Color(0xFFA3A3A3))
        : (_hovered ? Colors.black : const Color(0xFF525252));
    final border = on
        ? const Color(0xFF10B981).withValues(alpha: 0.4)
        : dark
        ? Colors.white.withValues(alpha: 0.1)
        : const Color(0xFFE5E5E5);
    final text = '${widget.count + (on ? 1 : 0)}';

    return Semantics(
      button: true,
      toggled: on,
      label: widget.semanticLabel == null ? null : '${widget.semanticLabel}, $text',
      child: FocusableActionDetector(
        mouseCursor: SystemMouseCursors.click,
        onShowFocusHighlight: (v) => setState(() => _focused = v),
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _toggle())},
        child: MouseRegion(
          onEnter: (_) => setState(() => _hovered = true),
          onExit: (_) => setState(() => _hovered = false),
          child: GestureDetector(
            onTap: _toggle,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              curve: const Cubic(0.4, 0, 0.2, 1),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: bg,
                borderRadius: const BorderRadius.all(Radius.circular(16)),
                border: Border.all(color: border),
                boxShadow: [if (_focused) BoxShadow(color: dark ? Colors.white54 : Colors.black45, spreadRadius: 2)],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  AnimatedBuilder(
                    animation: _icon,
                    builder: (context, child) =>
                        Transform.rotate(angle: _icon.value * 180 * math.pi / 180, child: child),
                    child: Icon(on ? Icons.repeat_rounded : Icons.repeat_rounded, size: 16, color: fg),
                  ),
                  const SizedBox(width: 8),
                  AnimatedDefaultTextStyle(
                    duration: const Duration(milliseconds: 150),
                    style: DefaultTextStyle.of(context).style
                        .merge(TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: fg)),
                    child: Text(text),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
