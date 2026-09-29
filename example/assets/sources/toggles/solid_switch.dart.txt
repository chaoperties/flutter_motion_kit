// SolidSwitch — a crisp high-contrast switch that inverts when on.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "Solid Switch" toggle (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   SolidSwitch()                                        // keeps its own state
//   SolidSwitch(value: on, onChanged: (v) => setState(() => on = v))

import 'package:flutter/material.dart';

class SolidSwitch extends StatefulWidget {
  const SolidSwitch({super.key, this.value, this.onChanged, this.initialValue = false, this.semanticLabel});

  /// Whether the switch is on. Leave null and the switch keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  /// What a screen reader announces, e.g. "Wi-Fi".
  final String? semanticLabel;

  @override
  State<SolidSwitch> createState() => _SolidSwitchState();
}

class _SolidSwitchState extends State<SolidSwitch> with SingleTickerProviderStateMixin {
  late bool _own = widget.initialValue;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Thumb position: 0 = off (left), 1 = on (right). Unbounded so springs can overshoot.
  late final AnimationController _thumb = AnimationController.unbounded(vsync: this, value: _on ? 1 : 0);

  @override
  void didUpdateWidget(SolidSwitch oldWidget) {
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
    _thumb.animateTo(target, duration: const Duration(milliseconds: 150), curve: Curves.easeOut);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final track = on
        ? (dark ? Colors.white : Colors.black)
        : (dark ? const Color(0xFF262626) : const Color(0xFFE5E5E5));
    final border = on ? null : (dark ? Colors.white.withValues(alpha: 0.1) : const Color(0xFFD4D4D4));
    const radius = BorderRadius.all(Radius.circular(16));

    final thumb = Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        color: (on != dark) ? Colors.white : Colors.black,
        borderRadius: const BorderRadius.all(Radius.circular(12)),
        boxShadow: const [BoxShadow(color: Color(0x0D000000), blurRadius: 2, offset: Offset(0, 1))],
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
                  border: Border.all(color: border ?? Colors.transparent),
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
