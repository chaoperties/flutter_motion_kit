// LikeToggle — a heart that pops with a burst of particles when liked.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Like Action" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   LikeToggle(count: 42)                              // shows 42, or 43 when on
//   LikeToggle(count: post.count, value: post.mine, onChanged: toggle)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class LikeToggle extends StatefulWidget {
  const LikeToggle({
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

  /// What a screen reader announces before the count, e.g. "Like".
  final String? semanticLabel;

  @override
  State<LikeToggle> createState() => _LikeToggleState();
}

class _LikeToggleState extends State<LikeToggle> with SingleTickerProviderStateMixin {
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
  void didUpdateWidget(LikeToggle oldWidget) {
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
        ? const Color(0xFFF43F5E).withValues(alpha: 0.2)
        : dark
        ? Colors.white.withValues(alpha: 0.05)
        : const Color(0xFFF5F5F5);
    final fg = on
        ? const Color(0xFFFB7185)
        : dark
        ? (_hovered ? Colors.white : const Color(0xFFA3A3A3))
        : (_hovered ? Colors.black : const Color(0xFF525252));
    final border = on
        ? const Color(0xFFF43F5E).withValues(alpha: 0.4)
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
                        Transform.scale(scale: _keyframes(const [1, 1.4, 1], _icon.value), child: child),
                    child: CustomPaint(
                      painter: _BurstPainter(_icon.isAnimating ? _icon.value * 1.6 : 1, const Color(0xFFF43F5E)),
                      child: Icon(
                        on ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                        size: 16,
                        color: on ? const Color(0xFFF43F5E) : fg,
                      ),
                    ),
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

/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = x.floor().clamp(0, segments - 1);
  return values[i] + (values[i + 1] - values[i]) * Curves.easeInOut.transform(x - i);
}

/// Six dots flying out of the icon and fading, drawn around its centre.
class _BurstPainter extends CustomPainter {
  _BurstPainter(this.t, this.color);

  final double t;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    if (t <= 0 || t >= 1) return;
    final centre = size.center(Offset.zero);
    final ease = Curves.easeOut.transform(t);
    final paint = Paint()..color = color.withValues(alpha: 1 - t);
    for (var i = 0; i < 6; i++) {
      final angle = i * math.pi / 3 - math.pi / 2;
      final distance = 6 + 10 * ease;
      canvas.drawCircle(centre + Offset(math.cos(angle), math.sin(angle)) * distance, 2 * (1 - t), paint);
    }
  }

  @override
  bool shouldRepaint(_BurstPainter old) => old.t != t || old.color != color;
}
