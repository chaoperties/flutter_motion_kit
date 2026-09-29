// MotionButton — a pill button with one of eleven micro-interactions.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's AnimatedButton (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   // Decorative: the effect plays on hover.
//   MotionButton(label: 'Settings', icon: Icons.settings_outlined, effect: MotionButtonEffect.rotate)
//
//   // Action with feedback: the effect confirms the press, never before it.
//   MotionButton(
//     label: 'Copy hash',
//     activeLabel: 'Copied',
//     icon: Icons.copy_rounded,
//     icon2: Icons.check_rounded,
//     icon2Color: Colors.greenAccent,
//     trigger: MotionButtonTrigger.press,
//     onPressed: () => Clipboard.setData(ClipboardData(text: hash)),
//   )
//
// Every button lifts slightly on hover (desktop/web) and keyboard focus, and presses in on tap.

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/physics.dart';

enum MotionButtonEffect {
  /// Leading icon slides out, trailing [MotionButton.icon2] slides in.
  slideArrow,

  /// Icon swaps upward to [MotionButton.icon2] with two little stars popping out.
  sparkle,

  /// Icon cross-scales into [MotionButton.icon2]; label can switch to [MotionButton.activeLabel].
  morph,

  /// Icon beats once and swaps to its filled [MotionButton.icon2] in [MotionButton.iconColor].
  pulse,

  /// Icon turns half a revolution.
  rotate,

  /// Icon wiggles; icon and label tint to [MotionButton.iconColor] (e.g. red for delete).
  shake,

  /// Icon tilts into [MotionButton.icon2] and a notification dot pops in.
  ring,

  /// A light streak sweeps across the button, repeating while hovered.
  glare,

  /// Label rolls up to reveal itself again; icon turns 45 degrees.
  textReveal,

  /// Button follows the pointer a little.
  magnetic,

  /// A ring ripples outward from the button edge.
  expandRing,
}

/// When the effect's active state (second icon, [MotionButton.activeLabel], tint) shows.
enum MotionButtonTrigger {
  /// While hovered or keyboard-focused. For decorative effects that don't claim anything happened.
  hover,

  /// After a press, for [MotionButton.confirmDuration]. For actions whose active state
  /// reports a result — Copied, Liked, Saved — so it never shows before the user acts.
  press,
}

class MotionButton extends StatefulWidget {
  const MotionButton({
    super.key,
    required this.label,
    required this.icon,
    this.icon2,
    this.effect = MotionButtonEffect.morph,
    this.onPressed,
    this.iconColor,
    this.icon2Color,
    this.activeLabel,
    this.trigger = MotionButtonTrigger.hover,
    this.stayActive = const Duration(milliseconds: 500),
    this.confirmDuration = const Duration(milliseconds: 1500),
  });

  final String label;
  final IconData icon;

  /// Second icon used by slideArrow, sparkle, morph, pulse and ring.
  final IconData? icon2;

  final MotionButtonEffect effect;
  final VoidCallback? onPressed;

  /// Tint for [icon] while active (pulse, shake).
  final Color? iconColor;

  /// Tint for [icon2].
  final Color? icon2Color;

  /// Label shown while active, e.g. 'Copied'. If it reports a result, use [MotionButtonTrigger.press].
  final String? activeLabel;

  /// What makes the effect active. Defaults to hover.
  final MotionButtonTrigger trigger;

  /// Hover trigger with an [activeLabel]: how long the active state lingers after the pointer leaves.
  final Duration stayActive;

  /// Press trigger: how long the active state is shown after each press.
  final Duration confirmDuration;

  @override
  State<MotionButton> createState() => _MotionButtonState();
}

/// Maps a damped spring onto a [Curve] so implicit animations can bounce like Motion's springs.
class _SpringCurve extends Curve {
  _SpringCurve(double stiffness, double damping)
    : _sim = SpringSimulation(SpringDescription(mass: 1, stiffness: stiffness, damping: damping), 0, 1, 0),
      // Time for the oscillation to decay below 1%: e^(-damping/2 * t) = 0.01.
      seconds = 9.2 / damping;

  final SpringSimulation _sim;
  final double seconds;

  Duration get duration => Duration(microseconds: (seconds * 1e6).round());

  @override
  double transformInternal(double t) => _sim.x(t * seconds);
}

final _snappy = _SpringCurve(600, 25);
final _soft = _SpringCurve(400, 25);
final _press = _SpringCurve(500, 25);

class _MotionButtonState extends State<MotionButton> with TickerProviderStateMixin {
  bool _hovered = false;
  bool _pressed = false;
  bool _latched = false; // hover trigger: stays active briefly after leaving
  bool _confirmed = false; // press trigger: active for a moment after each press
  Offset _magnet = Offset.zero;
  Timer? _latchTimer;
  Timer? _touchTimer;
  Timer? _confirmTimer;

  // One-shot keyframe effects (pulse, shake, expandRing).
  late final AnimationController _oneShot = AnimationController(vsync: this, duration: _oneShotDuration);
  // Repeating glare sweep: 0.85s sweep + 1s pause.
  late final AnimationController _glare = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1850),
  );

  Duration get _oneShotDuration => widget.effect == MotionButtonEffect.expandRing
      ? const Duration(milliseconds: 600)
      : const Duration(milliseconds: 400);

  bool get _onPress => widget.trigger == MotionButtonTrigger.press;

  bool get _active => _onPress ? _confirmed : (_hovered || _latched);

  @override
  void dispose() {
    _latchTimer?.cancel();
    _touchTimer?.cancel();
    _confirmTimer?.cancel();
    _oneShot.dispose();
    _glare.dispose();
    super.dispose();
  }

  void _enter() {
    if (_hovered) return;
    _latchTimer?.cancel();
    setState(() {
      _hovered = true;
      if (!_onPress && widget.activeLabel != null) _latched = true;
    });
    if (!_onPress) _oneShot.forward(from: 0);
    // Glare and magnetic have no "result" to report, so they always follow the pointer.
    if (widget.effect == MotionButtonEffect.glare) _glare.repeat();
  }

  void _exit() {
    if (!_hovered) return;
    setState(() {
      _hovered = false;
      _magnet = Offset.zero;
    });
    _glare
      ..stop()
      ..value = 0;
    if (_latched) {
      _latchTimer = Timer(widget.stayActive, () {
        if (mounted && !_hovered) setState(() => _latched = false);
      });
    }
  }

  void _handlePress() {
    widget.onPressed?.call();
    if (!_onPress) return;
    _confirmTimer?.cancel();
    setState(() => _confirmed = true);
    _oneShot.forward(from: 0);
    _confirmTimer = Timer(widget.confirmDuration, () {
      if (mounted) setState(() => _confirmed = false);
    });
  }

  void _hover(PointerHoverEvent e) {
    if (widget.effect != MotionButtonEffect.magnetic) return;
    final size = context.size;
    if (size == null) return;
    setState(() => _magnet = (e.localPosition - size.center(Offset.zero)) * 0.35);
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final fg = dark ? const Color(0xFFE3E3E3) : Colors.black;
    final fill = (dark ? Colors.white : Colors.black).withValues(
      alpha: (_latched || _confirmed) ? 0.08 : (_hovered ? 0.06 : 0.04),
    );
    final scale = _pressed ? 0.96 : (_hovered ? 1.02 : 1.0);

    Widget button = AnimatedContainer(
      duration: _press.duration,
      curve: _press,
      height: 36,
      constraints: const BoxConstraints(minWidth: 36),
      padding: EdgeInsets.symmetric(horizontal: _hovered ? 28 : 24),
      decoration: BoxDecoration(color: fill, borderRadius: BorderRadius.circular(40)),
      clipBehavior: widget.effect == MotionButtonEffect.glare ? Clip.antiAlias : Clip.none,
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          AnimatedSize(
            duration: _press.duration,
            curve: _press,
            child: DefaultTextStyle.merge(
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, letterSpacing: -0.2, color: fg),
              child: IconTheme(
                data: IconThemeData(size: 16, color: fg),
                child: Row(mainAxisSize: MainAxisSize.min, children: _content(fg)),
              ),
            ),
          ),
          if (widget.effect == MotionButtonEffect.glare) Positioned.fill(child: _GlareSweep(_glare, dark)),
        ],
      ),
    );

    if (widget.effect == MotionButtonEffect.expandRing) {
      button = Stack(
        clipBehavior: Clip.none,
        children: [
          button,
          Positioned.fill(
            child: IgnorePointer(
              child: AnimatedBuilder(
                animation: _oneShot,
                builder: (context, _) {
                  final t = Curves.easeOut.transform(_oneShot.value);
                  if (_oneShot.value == 0 || _oneShot.value == 1) return const SizedBox();
                  return Transform.scale(
                    scale: 1 + 0.15 * t,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(40),
                        border: Border.all(color: fg.withValues(alpha: 0.25 * (1 - t))),
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      );
    }

    return Semantics(
      button: true,
      // Announce "Copied" etc. to screen readers when a press confirms.
      liveRegion: _onPress && widget.activeLabel != null,
      label: _active && widget.activeLabel != null ? widget.activeLabel : widget.label,
      child: FocusableActionDetector(
        // Keyboard focus plays the effect too, but only when focus is visible (keyboard use).
        onShowFocusHighlight: (v) => v ? _enter() : _exit(),
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _handlePress())},
        child: MouseRegion(
          cursor: SystemMouseCursors.click,
          onEnter: (_) => _enter(),
          onExit: (_) => _exit(),
          onHover: _hover,
          child: GestureDetector(
            onTapDown: (_) {
              _touchTimer?.cancel();
              setState(() => _pressed = true);
              _enter();
            },
            onTapUp: (d) {
              setState(() => _pressed = false);
              // Touch has no hover-out, so release the active state shortly after lift-off.
              if (d.kind == PointerDeviceKind.touch) {
                _touchTimer = Timer(const Duration(milliseconds: 500), _exit);
              }
            },
            onTapCancel: () => setState(() => _pressed = false),
            onTap: _handlePress,
            child: TweenAnimationBuilder<Offset>(
              tween: Tween(end: _magnet),
              duration: _soft.duration,
              curve: _soft,
              builder: (context, offset, child) => Transform.translate(offset: offset, child: child),
              child: AnimatedScale(scale: scale, duration: _press.duration, curve: _press, child: button),
            ),
          ),
        ),
      ),
    );
  }

  List<Widget> _content(Color fg) {
    final label = Text(
      _active && widget.activeLabel != null ? widget.activeLabel! : widget.label,
      maxLines: 1,
      softWrap: false,
    );
    const gap = SizedBox(width: 10);
    final icon2 = Icon(widget.icon2 ?? widget.icon, color: widget.icon2Color);

    switch (widget.effect) {
      case MotionButtonEffect.slideArrow:
        return [
          _SlideSlot(visible: !_active, fromLeft: true, child: Icon(widget.icon)),
          label,
          _SlideSlot(visible: _active, fromLeft: false, child: icon2),
        ];

      case MotionButtonEffect.sparkle:
        return [
          _IconSwap(active: _active, kind: _SwapKind.sparkle, a: Icon(widget.icon), b: icon2),
          gap,
          label,
        ];

      case MotionButtonEffect.morph:
        return [
          _IconSwap(active: _active, kind: _SwapKind.morph, a: Icon(widget.icon), b: icon2),
          gap,
          label,
        ];

      case MotionButtonEffect.ring:
        return [_IconSwap(active: _active, kind: _SwapKind.ring, a: Icon(widget.icon), b: icon2), gap, label];

      case MotionButtonEffect.pulse:
        final tint = widget.iconColor ?? fg;
        return [
          AnimatedBuilder(
            animation: _oneShot,
            builder: (context, _) => Transform.scale(
              scale: _keyframes(const [1, 1.25, 1], _oneShot.value, Curves.easeInOut),
              child: Icon(_active ? (widget.icon2 ?? widget.icon) : widget.icon, color: _active ? tint : fg),
            ),
          ),
          gap,
          label,
        ];

      case MotionButtonEffect.rotate:
        return [
          AnimatedRotation(
            turns: _active ? 0.5 : 0,
            duration: _soft.duration,
            curve: _soft,
            child: Icon(widget.icon),
          ),
          gap,
          label,
        ];

      case MotionButtonEffect.shake:
        final tint = _active ? (widget.iconColor ?? fg) : fg;
        return [
          AnimatedBuilder(
            animation: _oneShot,
            builder: (context, _) {
              final t = _oneShot.value;
              return Transform.translate(
                offset: Offset(0, _keyframes(const [0, -2, 0, -2, 0], t, Curves.linear)),
                child: Transform.rotate(
                  angle: _keyframes(const [0, -10, 10, -10, 0], t, Curves.linear) * math.pi / 180,
                  child: Icon(widget.icon, color: tint),
                ),
              );
            },
          ),
          gap,
          AnimatedDefaultTextStyle(
            duration: const Duration(milliseconds: 300),
            style: DefaultTextStyle.of(context).style.merge(
              TextStyle(fontSize: 13, fontWeight: FontWeight.w500, letterSpacing: -0.2, color: tint),
            ),
            child: label,
          ),
        ];

      case MotionButtonEffect.textReveal:
        return [
          AnimatedRotation(
            turns: _active ? 0.125 : 0,
            duration: _soft.duration,
            curve: _soft,
            child: Icon(widget.icon),
          ),
          gap,
          ClipRect(
            child: TweenAnimationBuilder<double>(
              tween: Tween(end: _active ? -18 : 0),
              duration: _soft.duration,
              curve: _soft,
              builder: (context, dy, child) => Transform.translate(offset: Offset(0, dy), child: child),
              // The label sits on top of a copy of itself; rolling up reveals the copy.
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  SizedBox(height: 18, child: Center(child: label)),
                  Positioned(left: 0, right: 0, top: 18, height: 18, child: Center(child: label)),
                ],
              ),
            ),
          ),
        ];

      case MotionButtonEffect.glare:
      case MotionButtonEffect.magnetic:
        return [Icon(widget.icon), gap, label];

      case MotionButtonEffect.expandRing:
        return [
          AnimatedScale(
            scale: _active ? 1.1 : 1,
            duration: _press.duration,
            curve: _SpringCurve(400, 20),
            child: Icon(widget.icon),
          ),
          gap,
          label,
        ];
    }
  }
}

/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t, Curve curve) {
  if (t <= 0) return values.first;
  if (t >= 1) return values.last;
  final segments = values.length - 1;
  final i = math.min((t * segments).floor(), segments - 1);
  final local = curve.transform(t * segments - i);
  return values[i] + (values[i + 1] - values[i]) * local;
}

/// An icon slot that collapses to zero width and slides/fades when hidden.
class _SlideSlot extends StatelessWidget {
  const _SlideSlot({required this.visible, required this.fromLeft, required this.child});

  final bool visible;
  final bool fromLeft;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(end: visible ? 1 : 0),
      duration: _snappy.duration,
      curve: _snappy,
      builder: (context, t, child) {
        final c = t.clamp(0.0, 1.0);
        return ClipRect(
          child: Align(
            alignment: fromLeft ? Alignment.centerRight : Alignment.centerLeft,
            widthFactor: c,
            child: Opacity(
              opacity: c,
              child: Transform.translate(
                offset: Offset((fromLeft ? -10 : 10) * (1 - t), 0),
                child: Padding(
                  padding: EdgeInsets.only(left: fromLeft ? 0 : 10, right: fromLeft ? 10 : 0),
                  child: child,
                ),
              ),
            ),
          ),
        );
      },
      child: child,
    );
  }
}

enum _SwapKind { morph, sparkle, ring }

/// Swaps two icons in a fixed 16x16 box, with an effect-specific enter/exit.
class _IconSwap extends StatelessWidget {
  const _IconSwap({required this.active, required this.kind, required this.a, required this.b});

  final bool active;
  final _SwapKind kind;
  final Widget a;
  final Widget b;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 16,
      height: 16,
      child: AnimatedSwitcher(
        duration: _snappy.duration,
        switchInCurve: _snappy,
        switchOutCurve: Curves.easeOut,
        layoutBuilder: (current, previous) =>
            Stack(clipBehavior: Clip.none, alignment: Alignment.center, children: [...previous, ?current]),
        transitionBuilder: (child, animation) {
          final isB = child.key == const ValueKey('b');
          return AnimatedBuilder(
            animation: animation,
            child: child,
            builder: (context, child) {
              final t = animation.value;
              final hidden = 1 - t;
              final opacity = t.clamp(0.0, 1.0);
              switch (kind) {
                case _SwapKind.morph:
                  return Opacity(
                    opacity: opacity,
                    child: Transform.scale(scale: 0.5 + 0.5 * t, child: child),
                  );
                case _SwapKind.sparkle:
                  // Old icon leaves upward, new icon rises from below.
                  final dy = (isB ? 15.0 : -15.0) * hidden;
                  return Opacity(
                    opacity: opacity,
                    child: Transform.translate(
                      offset: Offset(0, dy),
                      child: Transform.scale(scale: 0.8 + 0.2 * t, child: child),
                    ),
                  );
                case _SwapKind.ring:
                  return Opacity(
                    opacity: opacity,
                    child: Transform.rotate(
                      angle: -15 * hidden * math.pi / 180,
                      child: Transform.scale(scale: 0.8 + 0.2 * t, child: child),
                    ),
                  );
              }
            },
          );
        },
        child: active
            ? Stack(
                key: const ValueKey('b'),
                clipBehavior: Clip.none,
                alignment: Alignment.center,
                children: [
                  b,
                  if (kind == _SwapKind.sparkle) ...[
                    const _Pop(delay: 50, top: -12, right: -8, size: 10, color: Color(0xFFFEF08A)),
                    const _Pop(delay: 100, top: -4, left: -12, size: 6, color: Color(0xFFFACC15)),
                  ],
                  if (kind == _SwapKind.ring) const _Pop(delay: 100, top: 0, right: 0, size: 6, dot: true),
                ],
              )
            : KeyedSubtree(key: const ValueKey('a'), child: a),
      ),
    );
  }
}

/// A small star (or dot) that springs in after [delay] ms.
class _Pop extends StatefulWidget {
  const _Pop({
    required this.delay,
    required this.size,
    this.top,
    this.left,
    this.right,
    this.color = const Color(0xFFEF4444),
    this.dot = false,
  });

  final int delay;
  final double size;
  final double? top, left, right;
  final Color color;
  final bool dot;

  @override
  State<_Pop> createState() => _PopState();
}

class _PopState extends State<_Pop> {
  bool _shown = false;
  late final Timer _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer(Duration(milliseconds: widget.delay), () => setState(() => _shown = true));
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final curve = widget.dot ? _SpringCurve(600, 15) : _snappy;
    return Positioned(
      top: widget.top,
      left: widget.left,
      right: widget.right,
      child: TweenAnimationBuilder<double>(
        tween: Tween(end: _shown ? 1 : 0),
        duration: curve.duration,
        curve: curve,
        builder: (context, t, _) => Transform.rotate(
          angle: widget.dot ? 0 : (1 - t) * -math.pi / 4,
          child: Transform.scale(
            scale: math.max(0, t),
            child: widget.dot
                ? Container(
                    width: widget.size,
                    height: widget.size,
                    decoration: BoxDecoration(color: widget.color, shape: BoxShape.circle),
                  )
                : Icon(Icons.star_rounded, size: widget.size + 2, color: widget.color),
          ),
        ),
      ),
    );
  }
}

class _GlareSweep extends StatelessWidget {
  const _GlareSweep(this.animation, this.dark);

  final Animation<double> animation;
  final bool dark;

  @override
  Widget build(BuildContext context) {
    final shine = dark ? Colors.white.withValues(alpha: 0.22) : Colors.black.withValues(alpha: 0.12);
    return IgnorePointer(
      child: LayoutBuilder(
        builder: (context, box) => AnimatedBuilder(
          animation: animation,
          builder: (context, _) {
            // First 0.85s of the 1.85s cycle is the sweep; the rest is a pause.
            final sweep = (animation.value * 1.85 / 0.85).clamp(0.0, 1.0);
            if (animation.value == 0) return const SizedBox();
            final t = Curves.easeInOut.transform(sweep);
            // The 50px streak travels from -150% to +150% of its own width around the centre.
            final x = box.maxWidth / 2 - 25 + (-75 + 150 * t);
            return Stack(
              children: [
                Positioned(
                  left: x,
                  top: -10,
                  bottom: -10,
                  width: 50,
                  child: Transform(
                    transform: Matrix4.skewX(-20 * math.pi / 180),
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [shine.withValues(alpha: 0), shine, shine.withValues(alpha: 0)],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
