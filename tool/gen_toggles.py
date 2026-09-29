# Generates lib/widgets/toggles/*.dart (except pill_tabs.dart, which is hand-written),
# plus the gallery catalogue, a test table and exports.
#
# Each toggle must stand alone (copy-paste rule), so the shared machinery
# (state handling, keyboard/focus, springs) is written into every file rather
# than imported. Edit a toggle in SWITCHES or ACTIONS, then run:
#
#   python tool/gen_toggles.py
#
# (it runs `dart format` on what it wrote, so dart must be on the PATH).
#
# Sizes, colours and motion follow Amicro's AnimatedToggle one to one, except the
# Double Bounce Switch: Amicro's version depends on CSS that isn't in its repo, so
# its bounce is designed here.
import os
import re
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'lib', 'widgets', 'toggles')

# Tailwind colours used by Amicro.
C = {
    'white': 'Colors.white', 'black': 'Colors.black',
    'n100': 'Color(0xFFF5F5F5)', 'n200': 'Color(0xFFE5E5E5)', 'n300': 'Color(0xFFD4D4D4)',
    'n400': 'Color(0xFFA3A3A3)', 'n600': 'Color(0xFF525252)', 'n700': 'Color(0xFF404040)',
    'n800': 'Color(0xFF262626)', 'n900': 'Color(0xFF171717)',
    'emerald500': 'Color(0xFF10B981)', 'emerald600': 'Color(0xFF059669)', 'emerald400': 'Color(0xFF34D399)',
    'blue600': 'Color(0xFF2563EB)', 'blue500': 'Color(0xFF3B82F6)', 'blue400': 'Color(0xFF60A5FA)',
    'blue100': 'Color(0xFFDBEAFE)', 'blue300': 'Color(0xFF93C5FD)',
    'indigo500': 'Color(0xFF6366F1)', 'indigo600': 'Color(0xFF4F46E5)', 'indigo700': 'Color(0xFF4338CA)',
    'indigo900': 'Color(0xFF312E81)', 'indigo950': 'Color(0xFF1E1B4B)',
    'amber100': 'Color(0xFFFEF3C7)', 'amber300': 'Color(0xFFFCD34D)', 'amber400': 'Color(0xFFFBBF24)',
    'amber500': 'Color(0xFFF59E0B)', 'amber600': 'Color(0xFFD97706)', 'yellow300': 'Color(0xFFFDE047)',
    'rose400': 'Color(0xFFFB7185)', 'rose500': 'Color(0xFFF43F5E)',
}


def c(name, alpha=None):
    v = C[name]
    if not v.startswith('Colors.'):
        v = 'const ' + v
    return f'{v}.withValues(alpha: {alpha})' if alpha is not None else v


SHADOW_MD = '''const [
  BoxShadow(color: Color(0x1A000000), blurRadius: 6, spreadRadius: -1, offset: Offset(0, 4)),
  BoxShadow(color: Color(0x1A000000), blurRadius: 4, spreadRadius: -2, offset: Offset(0, 2)),
]'''
SHADOW_SM = 'const [BoxShadow(color: Color(0x0D000000), blurRadius: 2, offset: Offset(0, 1))]'

# ---------------------------------------------------------------------------
# Switches: a track with a thumb that travels from left to right.

SWITCHES = [
    dict(cls='DoubleBounceSwitch', label='Double Bounce Switch', desc='a switch whose thumb overshoots, bounces back and settles',
         size=(56, 32), radius='16', travel=24, thumb=(24, 24, '12'), shadow=SHADOW_MD, color_ms=150,
         motion=('keyframes', 520, [0, 1.12, 0.95, 1.03, 1]),
         track=f"on ? {c('emerald500')} : (dark ? {c('n800')} : {c('n300')})",
         thumb_color='Colors.white'),
    dict(cls='SolidSwitch', label='Solid Switch', desc='a crisp high-contrast switch that inverts when on',
         size=(56, 32), radius='16', travel=24, thumb=(24, 24, '12'), shadow=SHADOW_SM, color_ms=200,
         motion=('tween', 150, 'Curves.easeOut'),
         track=f"on ? (dark ? {c('white')} : {c('black')}) : (dark ? {c('n800')} : {c('n200')})",
         border=f"on ? null : (dark ? {c('white', 0.1)} : {c('n300')})",
         thumb_color=f"(on != dark) ? {c('white')} : {c('black')}"),
    dict(cls='RectangleSwitch', label='Rectangle Toggle', desc='a squarish switch with a spring-loaded square thumb',
         size=(56, 32), radius='6', travel=24, thumb=(20, 20, '2'), shadow=SHADOW_MD, color_ms=200,
         motion=('spring', 500, 30),
         track=f"on ? {c('blue600')} : (dark ? {c('n900')} : {c('n100')})",
         border=f"on ? {c('blue500')} : (dark ? {c('n700')} : {c('n300')})",
         thumb_color='Colors.white'),
    dict(cls='CircleSwitch', label='Circle Curve Toggle', desc='a round pill switch with spring momentum',
         size=(64, 36), radius='18', travel=28, thumb=(28, 28, '14'), shadow=SHADOW_MD, color_ms=300,
         motion=('spring', 450, 25),
         track=f"on ? {c('indigo500')} : (dark ? {c('n800')} : {c('n300')})",
         thumb_color='Colors.white'),
    dict(cls='ClassicSwitch', label='Classic Toggle', desc='the classic green switch on a stiff spring',
         size=(64, 36), radius='18', travel=28, thumb=(28, 28, '14'), shadow=SHADOW_MD, color_ms=300,
         motion=('spring', 500, 30),
         track=f"on ? {c('emerald500')} : (dark ? {c('n800')} : {c('n300')})",
         thumb_color='Colors.white'),
    dict(cls='MorphSwitch', label='Morph Toggle', desc='a lock that rolls across and unlocks',
         size=(64, 36), radius='18', travel=28, thumb=(28, 28, '14'), shadow=SHADOW_MD, color_ms=300,
         motion=('spring', 400, 25), rotate=180,
         track=f"on ? {c('indigo600')} : (dark ? {c('n800')} : {c('n300')})",
         thumb_color='Colors.white',
         thumb_child=f"Icon(on ? Icons.lock_open_rounded : Icons.lock_rounded, size: 16, color: on ? {c('indigo600')} : {c('n600')})"),
    dict(cls='CheckmarkSwitch', label='Checkmark Draw', desc='a switch that draws a checkmark on its thumb',
         size=(64, 36), radius='18', travel=28, thumb=(28, 28, '14'), shadow=SHADOW_MD, color_ms=300,
         motion=('spring', 500, 28),
         track=f"on ? {c('emerald500')} : (dark ? {c('n800')} : {c('n300')})",
         thumb_color='Colors.white',
         thumb_child=f"_Check(visible: on, color: {c('emerald600')})"),
    dict(cls='ThemeSwitch', label='Theme Toggle', desc='a sun that rolls over into a moon',
         size=(64, 36), radius='18', travel=28, thumb=(28, 28, '14'), shadow=SHADOW_MD, color_ms=300,
         motion=('spring', 350, 22), rotate=360,
         track=f"on ? {c('indigo950')} : {c('amber100')}",
         border=f"on ? {c('indigo700', 0.5)} : {c('amber300')}",
         thumb_color=f"on ? {c('indigo900')} : {c('amber400')}",
         thumb_child=f"Icon(on ? Icons.dark_mode_rounded : Icons.light_mode_rounded, size: 16, color: on ? {c('yellow300')} : Colors.white)"),
]

CHECK = '''
/// A checkmark that pops in and draws its stroke, like Amicro's SVG path.
class _Check extends StatefulWidget {
  const _Check({required this.visible, required this.color});

  final bool visible;
  final Color color;

  @override
  State<_Check> createState() => _CheckState();
}

class _CheckState extends State<_Check> with TickerProviderStateMixin {
  // Scale/opacity of the icon (a default Motion spring) and how much of the stroke is drawn.
  late final AnimationController _presence = AnimationController.unbounded(vsync: this, value: widget.visible ? 1 : 0);
  late final AnimationController _draw = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 250),
    value: widget.visible ? 1 : 0,
  );

  static const _spring = SpringDescription(mass: 1, stiffness: 500, damping: 25);

  @override
  void didUpdateWidget(_Check oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.visible == widget.visible) return;
    final target = widget.visible ? 1.0 : 0.0;
    _presence
        .animateWith(SpringSimulation(_spring, _presence.value, target, _presence.velocity))
        .whenComplete(() => _presence.value = target);
    // The stroke draws in on the way in and stays whole on the way out.
    if (widget.visible) _draw.forward(from: 0);
  }

  @override
  void dispose() {
    _presence.dispose();
    _draw.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([_presence, _draw]),
      builder: (context, _) {
        final v = _presence.value;
        if (v <= 0.001) return const SizedBox.square(dimension: 16);
        return Opacity(
          opacity: v.clamp(0.0, 1.0),
          child: Transform.scale(
            scale: v.clamp(0.0, 2.0),
            child: CustomPaint(size: const Size.square(16), painter: _CheckPainter(_draw.value, widget.color)),
          ),
        );
      },
    );
  }
}

class _CheckPainter extends CustomPainter {
  _CheckPainter(this.progress, this.color);

  final double progress;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    // SVG path "M20 6L9 17l-5-5" in a 24x24 box.
    final s = size.width / 24;
    final path = Path()
      ..moveTo(20 * s, 6 * s)
      ..lineTo(9 * s, 17 * s)
      ..lineTo(4 * s, 12 * s);
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5 * s
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    for (final metric in path.computeMetrics()) {
      canvas.drawPath(metric.extractPath(0, metric.length * progress), paint);
    }
  }

  @override
  bool shouldRepaint(_CheckPainter old) => old.progress != progress || old.color != color;
}
'''

KEYFRAME_SIM = '''
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
'''

HEADER = '''// CLS — DESC.
//
// Copy this file into your project. It depends only on Flutter itself.
// SOURCE
//
// Usage:
USAGE
'''


def header(cls, desc, source, usage):
    return HEADER.replace('CLS', cls).replace('DESC', desc).replace('SOURCE', source).replace('USAGE', usage)


def source_line(label):
    return f'Ported from Amicro\'s "{label}" toggle (MIT, (c) 2026 Syed Subhan Uddin).'


def switch_file(s):
    cls = s['cls']
    w, h = s['size']
    tw_, th, tr = s['thumb']
    motion = s['motion']
    pad = 4
    has_border = 'border' in s
    source = source_line(s['label'])
    if cls == 'DoubleBounceSwitch':
        source = ('Inspired by Amicro\'s "Double Bounce Switch" (MIT, (c) 2026 Syed Subhan Uddin);\n'
                  '// Amicro\'s bounce lives in CSS that isn\'t in its repo, so this bounce is our own.')
    usage = (f'//   {cls}()                                        // keeps its own state\n'
             f'//   {cls}(value: on, onChanged: (v) => setState(() => on = v))')

    if motion[0] == 'spring':
        motion_field = (f'  static const _spring = SpringDescription(mass: 1, stiffness: {motion[1]}, damping: {motion[2]});\n')
        animate = '''    _thumb
        .animateWith(SpringSimulation(_spring, _thumb.value, target, _thumb.velocity))
        // The spring stops within a hair of its target; land exactly on it.
        .whenComplete(() => _thumb.value = target);'''
    elif motion[0] == 'tween':
        motion_field = ''
        animate = f'''    _thumb.animateTo(target, duration: const Duration(milliseconds: {motion[1]}), curve: {motion[2]});'''
    else:
        kf = ', '.join(str(v) for v in motion[2])
        motion_field = ''
        animate = f'''    // Overshoot, bounce back, overshoot a little less, settle.
    _thumb.animateWith(_KeyframeSimulation(_thumb.value, target, {motion[1] / 1000}, const [{kf}]));'''

    rotate = s.get('rotate')
    transform = f'Matrix4.translationValues({s["travel"]} * v, 0, 0)'
    if rotate:
        transform = f'Matrix4.translationValues({s["travel"]} * v, 0, 0)..rotateZ(v * {rotate} * math.pi / 180)'

    border_code = ''
    if has_border:
        border_code = f'''
    final border = {s['border']};'''
    fallback = ' ?? Colors.transparent' if has_border and 'null' in s['border'] else ''
    border_deco = f'\n            border: Border.all(color: border{fallback}),' if has_border else ''
    inner_w = w - 2 * pad - (2 if has_border else 0)
    inner_h = h - 2 * pad - (2 if has_border else 0)

    child = s.get('thumb_child')
    thumb_child = f',\n        child: {child}' if child else ''
    thumb_center = '\n        alignment: Alignment.center,' if child else ''

    code = header(cls, s['desc'], source, usage) + f'''
IMPORTS

class {cls} extends StatefulWidget {{
  const {cls}({{super.key, this.value, this.onChanged, this.initialValue = false, this.semanticLabel}});

  /// Whether the switch is on. Leave null and the switch keeps its own state.
  final bool? value;

  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;

  /// The starting state when [value] is null.
  final bool initialValue;

  /// What a screen reader announces, e.g. "Wi-Fi".
  final String? semanticLabel;

  @override
  State<{cls}> createState() => _{cls}State();
}}

class _{cls}State extends State<{cls}> with SingleTickerProviderStateMixin {{
  late bool _own = widget.initialValue;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

  // Thumb position: 0 = off (left), 1 = on (right). Unbounded so springs can overshoot.
  late final AnimationController _thumb = AnimationController.unbounded(vsync: this, value: _on ? 1 : 0);
{motion_field}
  @override
  void didUpdateWidget({cls} oldWidget) {{
    super.didUpdateWidget(oldWidget);
    final was = oldWidget.value ?? _own;
    if (was != _on) _animate();
  }}

  @override
  void dispose() {{
    _thumb.dispose();
    super.dispose();
  }}

  void _toggle() {{
    final next = !_on;
    if (widget.value == null) {{
      setState(() => _own = next);
      _animate();
    }}
    widget.onChanged?.call(next);
  }}

  void _animate() {{
    final target = _on ? 1.0 : 0.0;
{animate}
  }}

  @override
  Widget build(BuildContext context) {{
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final track = {s['track']};{border_code}
    const radius = BorderRadius.all(Radius.circular({s['radius']}));

    final thumb = Container(
      width: {tw_},
      height: {th},{thumb_center}
      decoration: BoxDecoration(
        color: {s['thumb_color']},
        borderRadius: const BorderRadius.all(Radius.circular({tr})),
        boxShadow: {s['shadow']},
      ){thumb_child},
    );

    return Semantics(
      toggled: on,
      label: widget.semanticLabel,
      child: FocusableActionDetector(
        mouseCursor: SystemMouseCursors.click,
        onShowFocusHighlight: (v) => setState(() => _focused = v),
        actions: {{ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _toggle())}},
        child: GestureDetector(
          onTap: _toggle,
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: {s['color_ms']}),
                curve: const Cubic(0.4, 0, 0.2, 1),
                width: {w},
                height: {h},
                padding: const EdgeInsets.all({pad}),
                decoration: BoxDecoration(color: track, borderRadius: radius,{border_deco}),
                child: SizedBox(
                  width: {inner_w},
                  height: {inner_h},
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: AnimatedBuilder(
                      animation: _thumb,
                      builder: (context, child) {{
                        final v = _thumb.value;
                        return Transform(transform: {transform}, alignment: Alignment.center, child: child);
                      }},
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
  }}
}}
'''
    if child and '_Check(' in child:
        code += CHECK
    if motion[0] == 'keyframes':
        code += KEYFRAME_SIM
    return finish(code)


# ---------------------------------------------------------------------------
# Actions: pill buttons with an icon that reacts when switched on.

OFF_COLORS = {
    'bg': f"dark ? {c('white', 0.05)} : {c('n100')}",
    'fg': f"dark ? (_hovered ? Colors.white : {c('n400')}) : (_hovered ? Colors.black : {c('n600')})",
    'border': f"dark ? {c('white', 0.1)} : {c('n200')}",
}

ACTIONS = [
    dict(cls='BookmarkToggle', label='Bookmark Action', desc='a bookmark button that fills and pops when saved',
         pad='EdgeInsets.all(12)', weight=500, icons=('Icons.bookmark_rounded', 'Icons.bookmark_border_rounded'),
         text="on ? 'Saved' : 'Bookmark'", labels=True,
         on_bg=f"dark ? {c('blue500', 0.2)} : {c('blue100')}", on_fg=f"dark ? {c('blue400')} : {c('blue600')}",
         on_border=f"dark ? {c('blue500', 0.4)} : {c('blue300')}",
         anim=('scale', [1, 1.3, 1])),
    dict(cls='LikeToggle', label='Like Action', desc='a heart that pops with a burst of particles when liked',
         pad='EdgeInsets.symmetric(horizontal: 14, vertical: 10)', weight=600,
         icons=('Icons.favorite_rounded', 'Icons.favorite_border_rounded'), count=42,
         on_bg=f"{c('rose500', 0.2)}", on_fg=f"{c('rose400')}", on_border=f"{c('rose500', 0.4)}",
         icon_on_color=c('rose500'), anim=('scale', [1, 1.4, 1]), burst=True),
    dict(cls='DislikeToggle', label='Dislike Action', desc='a thumbs-down that wiggles when switched on',
         pad='EdgeInsets.all(10)', weight=500, icons=('Icons.thumb_down_rounded', 'Icons.thumb_down_outlined'),
         text="'Dislike'",
         on_bg=f"dark ? {c('amber500', 0.2)} : {c('amber100')}", on_fg=f"dark ? {c('amber400')} : {c('amber600')}",
         on_border=f"dark ? {c('amber500', 0.4)} : {c('amber300')}",
         anim=('rotate', [0, -15, 0])),
    dict(cls='RepostToggle', label='Repost Action', desc='a repost button whose arrows turn half a circle',
         pad='EdgeInsets.symmetric(horizontal: 14, vertical: 10)', weight=600,
         icons=('Icons.repeat_rounded', 'Icons.repeat_rounded'), count=18,
         on_bg=f"{c('emerald500', 0.2)}", on_fg=f"{c('emerald400')}", on_border=f"{c('emerald500', 0.4)}",
         anim=('turn', 180, 300)),
]

BURST = '''
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
'''

KEYFRAMES = '''
/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = x.floor().clamp(0, segments - 1);
  return values[i] + (values[i + 1] - values[i]) * Curves.easeInOut.transform(x - i);
}
'''


def action_file(a):
    cls = a['cls']
    count = a.get('count')
    anim = a['anim']
    usage = (f'//   {cls}()                                        // keeps its own state\n'
             f'//   {cls}(value: saved, onChanged: (v) => setState(() => saved = v))')
    if count is not None:
        usage = (f'//   {cls}(count: {count})                              // shows {count}, or {count + 1} when on\n'
                 f'//   {cls}(count: post.count, value: post.mine, onChanged: toggle)')

    params = ['this.value', 'this.onChanged', 'this.initialValue = false']
    fields = ['''  /// Whether the button is on. Leave null and the button keeps its own state.
  final bool? value;''', '''  /// Called with the new value on every tap (or Space/Enter when focused).
  final ValueChanged<bool>? onChanged;''', '''  /// The starting state when [value] is null.
  final bool initialValue;''']
    if count is not None:
        params.append('this.count = 0')
        fields.append('''  /// The count without this user's vote; one is added while the button is on.
  final int count;''')
    if a.get('labels'):
        params.append("this.label = 'Bookmark'")
        params.append("this.activeLabel = 'Saved'")
        fields.append('''  /// Text shown while off.
  final String label;''')
        fields.append('''  /// Text shown while on.
  final String activeLabel;''')
        text = "on ? widget.activeLabel : widget.label"
    elif count is not None:
        text = "'${widget.count + (on ? 1 : 0)}'"
        params.append('this.semanticLabel')
        fields.append(f'''  /// What a screen reader announces before the count, e.g. "{'Like' if 'Like' in cls else 'Repost'}".
  final String? semanticLabel;''')
    else:
        text = a['text']
    ctor = ', '.join(['super.key'] + params)
    field_block = '\n\n'.join(fields)

    if anim[0] == 'turn':
        controller = f'''  // Rotation of the arrows: 0 = off, 1 = half a turn.
  late final AnimationController _icon = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: {anim[2]}),
    value: _on ? 1 : 0,
  );'''
        react = '''    if (_on) {
      _icon.animateTo(1, curve: Curves.easeInOut);
    } else {
      _icon.animateBack(0, curve: Curves.easeInOut);
    }'''
        icon_transform = f'Transform.rotate(angle: _icon.value * {anim[1]} * math.pi / 180, child: child)'
    else:
        kf = ', '.join(str(v) for v in anim[1])
        controller = '''  // Plays once each time the button switches on (Motion's default 0.8s keyframes).
  late final AnimationController _icon = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 800),
    value: 1,
  );'''
        react = '''    if (_on) {
      _icon.forward(from: 0);
    } else if (_icon.isAnimating) {
      // Switched off mid-pop: finish quickly rather than jump.
      _icon.animateTo(1, duration: const Duration(milliseconds: 150));
    }'''
        if anim[0] == 'scale':
            icon_transform = f'Transform.scale(scale: _keyframes(const [{kf}], _icon.value), child: child)'
        else:
            icon_transform = f'Transform.rotate(angle: _keyframes(const [{kf}], _icon.value) * math.pi / 180, child: child)'

    icon_color = f"on ? {a['icon_on_color']} : fg" if 'icon_on_color' in a else 'fg'
    icon = f"Icon(on ? {a['icons'][0]} : {a['icons'][1]}, size: 16, color: {icon_color})"
    if a.get('burst'):
        icon = f'''CustomPaint(
                  painter: _BurstPainter(_icon.isAnimating ? _icon.value * 1.6 : 1, {a['icon_on_color']}),
                  child: {icon},
                )'''

    sem_label = ("widget.semanticLabel == null ? null : '${widget.semanticLabel}, $text'"
                 if count is not None else 'null')

    code = header(cls, a['desc'], source_line(a['label']), usage) + f'''
IMPORTS

class {cls} extends StatefulWidget {{
  const {cls}({{{ctor}}});

{field_block}

  @override
  State<{cls}> createState() => _{cls}State();
}}

class _{cls}State extends State<{cls}> with SingleTickerProviderStateMixin {{
  late bool _own = widget.initialValue;
  bool _hovered = false;
  bool _focused = false;

  bool get _on => widget.value ?? _own;

{controller}

  @override
  void didUpdateWidget({cls} oldWidget) {{
    super.didUpdateWidget(oldWidget);
    final was = oldWidget.value ?? _own;
    if (was != _on) _react();
  }}

  @override
  void dispose() {{
    _icon.dispose();
    super.dispose();
  }}

  void _toggle() {{
    final next = !_on;
    if (widget.value == null) {{
      setState(() => _own = next);
      _react();
    }}
    widget.onChanged?.call(next);
  }}

  void _react() {{
{react}
  }}

  @override
  Widget build(BuildContext context) {{
    final dark = Theme.of(context).brightness == Brightness.dark;
    final on = _on;
    final bg = on ? {a['on_bg']} : {OFF_COLORS['bg']};
    final fg = on ? {a['on_fg']} : {OFF_COLORS['fg']};
    final border = on ? {a['on_border']} : {OFF_COLORS['border']};
    final text = {text};

    return Semantics(
      button: true,
      toggled: on,
      label: {sem_label},
      child: FocusableActionDetector(
        mouseCursor: SystemMouseCursors.click,
        onShowFocusHighlight: (v) => setState(() => _focused = v),
        actions: {{ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _toggle())}},
        child: MouseRegion(
          onEnter: (_) => setState(() => _hovered = true),
          onExit: (_) => setState(() => _hovered = false),
          child: GestureDetector(
          onTap: _toggle,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            curve: const Cubic(0.4, 0, 0.2, 1),
            padding: const {a['pad']},
            decoration: BoxDecoration(
              color: bg,
              borderRadius: const BorderRadius.all(Radius.circular(16)),
              border: Border.all(color: border),
              boxShadow: [
                if (_focused) BoxShadow(color: dark ? Colors.white54 : Colors.black45, spreadRadius: 2),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedBuilder(
                  animation: _icon,
                  builder: (context, child) => {icon_transform},
                  child: {icon},
                ),
                const SizedBox(width: 8),
                AnimatedDefaultTextStyle(
                  duration: const Duration(milliseconds: 150),
                  style: DefaultTextStyle.of(context).style.merge(
                    TextStyle(fontSize: 12, fontWeight: FontWeight.w{a['weight']}, color: fg),
                  ),
                  child: Text(text),
                ),
              ],
            ),
          ),
          ),
        ),
      ),
    );
  }}
}}
'''
    if '_keyframes(' in code:
        code += KEYFRAMES
    if a.get('burst'):
        code += BURST
    return finish(code)


def imports(code):
    out = []
    if 'math.' in code:
        out += ["import 'dart:math' as math;", '']
    out.append("import 'package:flutter/material.dart';")
    if 'SpringSimulation(' in code:
        out.append("import 'package:flutter/physics.dart';")
    return '\n'.join(out)


def finish(code):
    code = code.replace('IMPORTS', imports(code))
    return re.sub(r'\n{3,}', '\n\n', code)


def file_name(cls):
    return re.sub(r'(?<=[a-zA-Z])(?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z])', '_', cls).lower()


# Gallery order follows Amicro's; ClassicSwitch (from Amicro's registry) goes last.
ORDER = ['DoubleBounceSwitch', 'SolidSwitch', 'RectangleSwitch', 'CircleSwitch', 'BookmarkToggle', 'LikeToggle',
         'DislikeToggle', 'RepostToggle', 'PillTabs', 'MorphSwitch', 'CheckmarkSwitch', 'ThemeSwitch', 'ClassicSwitch']
LABELS = {x['cls']: x['label'] for x in SWITCHES + ACTIONS}
LABELS['PillTabs'] = 'Pill Tabs Switcher'
GALLERY_ARGS = {'LikeToggle': 'count: 42', 'RepostToggle': 'count: 18'}


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        if old.endswith('.dart') and old != 'pill_tabs.dart':
            os.remove(os.path.join(OUT, old))
    for s in SWITCHES:
        with open(os.path.join(OUT, file_name(s['cls']) + '.dart'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(switch_file(s))
    for a in ACTIONS:
        with open(os.path.join(OUT, file_name(a['cls']) + '.dart'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(action_file(a))

    with open(os.path.join(ROOT, 'example', 'lib', 'toggle_catalog.g.dart'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_toggles.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('typedef ToggleEntry = ({String name, String source, WidgetBuilder builder});\n\n')
        fh.write('final List<ToggleEntry> toggleCatalog = [\n')
        for cls in ORDER:
            fh.write(f"  (name: {LABELS[cls]!r}, source: 'toggles/{file_name(cls)}.dart', "
                     f"builder: (_) => const {cls}({GALLERY_ARGS.get(cls, '')})),\n")
        fh.write('];\n')

    with open(os.path.join(ROOT, 'test', 'toggle_widgets.g.dart'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_toggles.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('/// Every on/off toggle, built controlled (value + onChanged) or uncontrolled (value null).\n')
        fh.write('final toggleWidgets = <String, Widget Function(bool? value, ValueChanged<bool>? onChanged)>{\n')
        for x in SWITCHES + ACTIONS:
            fh.write(f"  '{x['cls']}': (v, f) => {x['cls']}(value: v, onChanged: f),\n")
        fh.write('};\n')

    lib = os.path.join(ROOT, 'lib', 'flutter_motion_kit.dart')
    s = open(lib, encoding='utf-8').read()
    s = re.sub(r"export 'widgets/toggles/[^']+';\n", '', s).rstrip('\n') + '\n'
    s += ''.join(f"export 'widgets/toggles/{file_name(cls)}.dart';\n" for cls in ORDER)
    with open(lib, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)

    subprocess.run('dart format -l 120 lib/widgets/toggles lib/flutter_motion_kit.dart test/toggle_widgets.g.dart '
                   'example/lib/toggle_catalog.g.dart', shell=True, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    print(f'Generated {len(SWITCHES) + len(ACTIONS)} toggles')


if __name__ == '__main__':
    main()
