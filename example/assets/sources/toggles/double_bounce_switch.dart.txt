// DoubleBounceSwitch — a switch whose thumb overshoots, bounces back and settles.
//
// Copy this file into your project. It depends only on Flutter itself.
// Inspired by Amicro's "Double Bounce Switch" (MIT, (c) 2026 Syed Subhan Uddin);
// Amicro's bounce lives in CSS that isn't in its repo, so this bounce is our own.
//
// Usage:
//   DoubleBounceSwitch()                                        // keeps its own state
//   DoubleBounceSwitch(value: on, onChanged: (v) => setState(() => on = v))

import 'package:flutter/material.dart';

class DoubleBounceSwitch extends StatefulWidget {
  const DoubleBounceSwitch({super.key, this.value, this.onChanged, this.initialValue = false, this.semanticLabel});

  /// Whether the switch is on. Leave null and the switch keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  /// What a screen reader announces, e.g. "Wi-Fi".
  final String? semanticLabel;

  @override
  State<DoubleBounceSwitch> createState() => _DoubleBounceSwitchState();
}

class _DoubleBounceSwitchState extends State<DoubleBounceSwitch> with SingleTickerProviderStateMixin {
  late bool _own = widget.initialValue;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Thumb position: 0 = off (left), 1 = on (right). Unbounded so springs can overshoot.
  late final AnimationController _thumb = AnimationController.unbounded(vsync: this, value: _on ? 1 : 0);

  @override
  void didUpdateWidget(DoubleBounceSwitch oldWidget) {
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
    // Overshoot, bounce back, overshoot a little less, settle.
    _thumb.animateWith(_KeyframeSimulation(_thumb.value, target, 0.52, const [0, 1.12, 0.95, 1.03, 1]));
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final track = on ? const Color(0xFF10B981) : (dark ? const Color(0xFF262626) : const Color(0xFFD4D4D4));
    const radius = BorderRadius.all(Radius.circular(16));

    final thumb = Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.all(Radius.circular(12)),
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
                duration: const Duration(milliseconds: 150),
                curve: const Cubic(0.4, 0, 0.2, 1),
                width: 56,
                height: 32,
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(color: track, borderRadius: radius),
                child: SizedBox(
                  width: 48,
                  height: 24,
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

/// Moves from [from] to [to] through evenly spaced keyframes (fractions of the way),
/// each segment eased out. Used as a Simulation so the controller stays unbounded.
class _KeyframeSimulation extends Simulation {
  _KeyframeSimulation(this.from, this.to, this.seconds, this.keyframes);

  final double from;
  final double to;
  final double seconds;
  final List<double> keyframes;

  double _fraction(double time) {
    final segments = keyframes.length - 1;
    final x = (time / seconds).clamp(0.0, 1.0) * segments;
    final i = x.floor().clamp(0, segments - 1);
    return keyframes[i] + (keyframes[i + 1] - keyframes[i]) * Curves.easeOut.transform(x - i);
  }

  @override
  double x(double time) => from + (to - from) * _fraction(time);

  @override
  double dx(double time) => (x(time + 0.001) - x(time)) / 0.001;

  @override
  bool isDone(double time) => time >= seconds;
}
