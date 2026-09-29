// RectangleSwitch — a squarish switch with a spring-loaded square thumb.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Rectangle Toggle" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   RectangleSwitch()                                        // keeps its own state
//   RectangleSwitch(value: on, onChanged: (v) => setState(() => on = v))

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class RectangleSwitch extends StatefulWidget {
  const RectangleSwitch({super.key, this.value, this.onChanged, this.initialValue = false, this.semanticLabel});

  /// Whether the switch is on. Leave null and the switch keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  /// What a screen reader announces, e.g. "Wi-Fi".
  final String? semanticLabel;

  @override
  State<RectangleSwitch> createState() => _RectangleSwitchState();
}

class _RectangleSwitchState extends State<RectangleSwitch> with SingleTickerProviderStateMixin {
  late bool _own = widget.initialValue;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Thumb position: 0 = off (left), 1 = on (right). Unbounded so springs can overshoot.
  late final AnimationController _thumb = AnimationController.unbounded(vsync: this, value: _on ? 1 : 0);
  static const _spring = SpringDescription(mass: 1, stiffness: 500, damping: 30);

  @override
  void didUpdateWidget(RectangleSwitch oldWidget) {
    super.didUpdateWidget(oldWidget);
    final was = oldWidget.value ?? _own;
    if (was != _on) _animate();
  }

  @override
  void dispose() {
    _thumb.dispose();
    super.dispose();
  }

  void _toggle() {
    final next = !_on;
    if (widget.value == null) {
      setState(() => _own = next);
      _animate();
    }
    widget.onChanged?.call(next);
  }

  void _animate() {
    final target = _on ? 1.0 : 0.0;
    _thumb
        .animateWith(SpringSimulation(_spring, _thumb.value, target, _thumb.velocity))
        // The spring stops within a hair of its target; land exactly on it.
        .whenComplete(() => _thumb.value = target);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final track = on ? const Color(0xFF2563EB) : (dark ? const Color(0xFF171717) : const Color(0xFFF5F5F5));
    final border = on ? const Color(0xFF3B82F6) : (dark ? const Color(0xFF404040) : const Color(0xFFD4D4D4));
    const radius = BorderRadius.all(Radius.circular(6));

    final thumb = Container(
      width: 20,
      height: 20,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.all(Radius.circular(2)),
        boxShadow: const [
          BoxShadow(color: Color(0x1A000000), blurRadius: 6, spreadRadius: -1, offset: Offset(0, 4)),
          BoxShadow(color: Color(0x1A000000), blurRadius: 4, spreadRadius: -2, offset: Offset(0, 2)),
        ],
      ),
    );

    return Semantics(
      toggled: on,
      label: widget.semanticLabel,
      child: FocusableActionDetector(
        mouseCursor: SystemMouseCursors.click,
        onShowFocusHighlight: (v) => setState(() => _focused = v),
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _toggle())},
        child: GestureDetector(
          onTap: _toggle,
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                curve: const Cubic(0.4, 0, 0.2, 1),
                width: 56,
                height: 32,
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: track,
                  borderRadius: radius,
                  border: Border.all(color: border),
                ),
                child: SizedBox(
                  width: 46,
                  height: 22,
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: AnimatedBuilder(
                      animation: _thumb,
                      builder: (context, child) {
                        final v = _thumb.value;
                        return Transform(
                          transform: Matrix4.translationValues(24 * v, 0, 0),
                          alignment: Alignment.center,
                          child: child,
                        );
                      },
                      child: thumb,
                    ),
                  ),
                ),
              ),
              if (_focused)
                Positioned.fill(
                  left: -4,
                  top: -4,
                  right: -4,
                  bottom: -4,
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        borderRadius: radius + const BorderRadius.all(Radius.circular(4)),
                        border: Border.all(color: dark ? Colors.white54 : Colors.black45, width: 2),
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
