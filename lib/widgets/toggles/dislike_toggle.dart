// DislikeToggle — a thumbs-down that wiggles when switched on.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Dislike Action" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   DislikeToggle()                                        // keeps its own state
//   DislikeToggle(value: saved, onChanged: (v) => setState(() => saved = v))

import 'dart:math' as math;

import 'package:flutter/material.dart';

class DislikeToggle extends StatefulWidget {
  const DislikeToggle({super.key, this.value, this.onChanged, this.initialValue = false});

  /// Whether the button is on. Leave null and the button keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  @override
  State<DislikeToggle> createState() => _DislikeToggleState();
}

class _DislikeToggleState extends State<DislikeToggle> with SingleTickerProviderStateMixin {
  late bool _own = widget.initialValue;
  bool _hovered = false;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Plays once each time the button switches on (Motion's default 0.8s keyframes).
  late final AnimationController _icon = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 800),
    value: 1,
  );

  @override
  void didUpdateWidget(DislikeToggle oldWidget) {
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
      _icon.forward(from: 0);
    } else if (_icon.isAnimating) {
      // Switched off mid-pop: finish quickly rather than jump.
      _icon.animateTo(1, duration: const Duration(milliseconds: 150));
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final bg = on
        ? dark
              ? const Color(0xFFF59E0B).withValues(alpha: 0.2)
              : const Color(0xFFFEF3C7)
        : dark
        ? Colors.white.withValues(alpha: 0.05)
        : const Color(0xFFF5F5F5);
    final fg = on
        ? dark
              ? const Color(0xFFFBBF24)
              : const Color(0xFFD97706)
        : dark
        ? (_hovered ? Colors.white : const Color(0xFFA3A3A3))
        : (_hovered ? Colors.black : const Color(0xFF525252));
    final border = on
        ? dark
              ? const Color(0xFFF59E0B).withValues(alpha: 0.4)
              : const Color(0xFFFCD34D)
        : dark
        ? Colors.white.withValues(alpha: 0.1)
        : const Color(0xFFE5E5E5);
    final text = 'Dislike';

    return Semantics(
      button: true,
      toggled: on,
      label: null,
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
              padding: const EdgeInsets.all(10),
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
                    builder: (context, child) => Transform.rotate(
                      angle: _keyframes(const [0, -15, 0], _icon.value) * math.pi / 180,
                      child: child,
                    ),
                    child: Icon(on ? Icons.thumb_down_rounded : Icons.thumb_down_outlined, size: 16, color: fg),
                  ),
                  const SizedBox(width: 8),
                  AnimatedDefaultTextStyle(
                    duration: const Duration(milliseconds: 150),
                    style: DefaultTextStyle.of(context).style
                        .merge(TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: fg)),
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

/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = x.floor().clamp(0, segments - 1);
  return values[i] + (values[i + 1] - values[i]) * Curves.easeInOut.transform(x - i);
}
