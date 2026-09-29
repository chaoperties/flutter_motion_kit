# Generates lib/widgets/text/*.dart plus the gallery catalogue, a test table and exports.
#
# Each text animation must stand alone (copy-paste rule), so the shared engine
# (ticker, text splitting, pose helpers) is written into every file rather than
# imported. Edit an effect in EFFECTS, then run:
#
#   python tool/gen_text.py
#
# (it runs `dart format` on what it wrote, so dart must be on the PATH).
#
# Timings, eases and colours follow Amicro's AnimatedText gallery one to one.
import os
import re
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'lib', 'widgets', 'text')

# Tailwind colours used by Amicro, as (dark theme, light theme).
COLORS = {
    'plain': ('Colors.white', 'Colors.black'),
    'indigo': ('const Color(0xFF818CF8)', 'const Color(0xFF4F46E5)'),
    'emerald': ('const Color(0xFF34D399)', 'const Color(0xFF059669)'),
    'cyan': ('const Color(0xFF22D3EE)', 'const Color(0xFF0891B2)'),
    'pink': ('const Color(0xFFF472B6)', 'const Color(0xFFDB2777)'),
    'amber': ('const Color(0xFFFBBF24)', 'const Color(0xFFD97706)'),
    'purple': ('const Color(0xFFC084FC)', 'const Color(0xFF9333EA)'),
    'indigoLight': ('const Color(0xFFA5B4FC)', 'const Color(0xFF4F46E5)'),
}
COLOR_NAMES = {
    'plain': 'white or black', 'indigo': 'indigo', 'emerald': 'emerald', 'cyan': 'cyan',
    'pink': 'pink', 'amber': 'amber', 'purple': 'purple', 'indigoLight': 'indigo',
}

EXPO = 'Cubic(0.16, 1, 0.3, 1)'  # Amicro's ease: [0.16, 1, 0.3, 1]
EASE = 'Curves.easeInOut'  # Motion's default ease for a timed tween

CHAR = 'AMICRO UI'
WORDS = 'Design Motion Amicro'


def E(cls, label, cat, desc, mode, sample, kind, **kw):
    return dict(cls=cls, label=label, cat=cat, desc=desc, mode=mode, sample=sample, kind=kind, **kw)


def tw(ms, curve=EASE, stagger=0):
    return ('tween', ms, curve, stagger)


def spring(k, c, stagger=0):
    return ('spring', k, c, stagger)


EFFECTS = [
    # Featured
    E('DiaTextReveal', 'Dia Text Reveal', 'Featured', 'wipes in from the left while coming out of a blur',
      'text', 'DIA REVEAL', 'enter', time=tw(850, EXPO), size=24, weight=900, spacing=-0.05, unit='wipe', blur=8),
    # Reveals
    E('BlurText', 'Blur Text', 'Reveals', 'comes into focus from a blur while scaling up', 'text', 'BLUR REVEAL',
      'enter', time=tw(700, EXPO), props=dict(opacity=(0, 1), scale=(0.9, 1)), blur=12),
    E('ShimmerText', 'Shimmer Text', 'Reveals', 'a soft gradient highlight that gently pulses', 'text',
      'SHIMMER TEXT', 'loop', loop=(2000, 0), weight=800, unit='shimmer'),
    E('TypewriterText', 'Typewriter Text', 'Reveals', 'typed out behind a cursor', 'text', 'TYPEWRITER', 'enter',
      time=tw(1200), size=18, color='emerald', unit='typewriter', gallery_style="fontFamily: 'JetBrainsMono'"),
    E('RevealText', 'Reveal Text', 'Reveals', 'a cinematic left-to-right wipe', 'text', 'CINEMATIC', 'enter',
      time=tw(750, EXPO), unit='wipe'),
    E('FadeInChar', 'Fade In Char', 'Reveals', 'characters fade in one after another', 'char', CHAR, 'enter',
      time=tw(300, stagger=50), props=dict(opacity=(0, 1))),
    E('FadeInWord', 'Fade In Word', 'Reveals', 'words fade in one after another', 'word', WORDS, 'enter',
      time=tw(400, stagger=150), props=dict(opacity=(0, 1))),
    E('FadeInText', 'Fade In Text', 'Reveals', 'the whole text fades in', 'text', 'FADE IN TEXT', 'enter',
      time=tw(800), props=dict(opacity=(0, 1))),
    E('BlurUpWord', 'Blur Up Word', 'Reveals', 'words rise into focus from a blur', 'word', WORDS, 'enter',
      time=tw(500, stagger=120), color='indigo', props=dict(opacity=(0, 1), y=(15, 0)), blur=8),
    E('BlurUpChar', 'Blur Up Char', 'Reveals', 'characters rise into focus from a blur', 'char', CHAR, 'enter',
      time=tw(400, stagger=40), color='indigo', props=dict(opacity=(0, 1), y=(15, 0)), blur=8),
    # Slide & Drop
    E('StaggerText', 'Stagger Text', 'Slide & Drop', 'words float up in a staggered sequence', 'word', WORDS,
      'enter', time=tw(500, EXPO, 100), props=dict(opacity=(0, 1), y=(20, 0))),
    E('SlideUpChar', 'Slide Up Char', 'Slide & Drop', 'characters slide up out of a hidden baseline', 'char', CHAR,
      'enter', time=tw(400, EXPO, 40), props=dict(yFrac=(1, 0)), clip='unit'),
    E('SlideUpWord', 'Slide Up Word', 'Slide & Drop', 'words slide up out of a hidden baseline', 'word', WORDS,
      'enter', time=tw(500, EXPO, 100), props=dict(yFrac=(1, 0)), clip='unit'),
    E('SlideUpText', 'Slide Up Text', 'Slide & Drop', 'the text block slides up out of a hidden baseline', 'text',
      'SLIDE UP TEXT', 'enter', time=tw(600, EXPO), props=dict(yFrac=(1, 0)), clip='unit'),
    E('SlideDownChar', 'Slide Down Char', 'Slide & Drop', 'characters drop down from a hidden top edge', 'char',
      CHAR, 'enter', time=tw(400, EXPO, 40), props=dict(yFrac=(-1, 0)), clip='unit'),
    E('SlideDownWord', 'Slide Down Word', 'Slide & Drop', 'words drop down from a hidden top edge', 'word', WORDS,
      'enter', time=tw(500, EXPO, 100), props=dict(yFrac=(-1, 0)), clip='unit'),
    E('SlideLeftChar', 'Slide Left Char', 'Slide & Drop', 'characters slide in from the right', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), x=(40, 0)), clip='all'),
    E('SlideRightChar', 'Slide Right Char', 'Slide & Drop', 'characters slide in from the left', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), x=(-40, 0)), clip='all'),
    E('DropInChar', 'Drop In Char', 'Slide & Drop', 'characters drop in from above on a spring', 'char', CHAR,
      'enter', time=spring(500, 25, 40), color='cyan', props=dict(opacity=(0, 1), y=(-50, 0))),
    E('RiseUpWord', 'Rise Up Word', 'Slide & Drop', 'words rise up and grow on a spring', 'word', WORDS, 'enter',
      time=spring(400, 22, 120), color='emerald', props=dict(opacity=(0, 1), y=(30, 0), scale=(0.8, 1))),
    E('BounceInChar', 'Bounce In Char', 'Slide & Drop', 'characters pop in, overshoot and settle', 'char', CHAR,
      'enter', time=tw(500, stagger=50), color='pink',
      props=dict(opacity=(0, 1), scale='_keyframes(const [0, 1.3, 1], t)')),
    # Scale & Zoom
    E('ScaleInChar', 'Scale In Char', 'Scale & Zoom', 'characters spring up from nothing', 'char', CHAR, 'enter',
      time=spring(450, 22, 40), props=dict(scale=(0, 1))),
    E('ScaleInWord', 'Scale In Word', 'Scale & Zoom', 'words grow into place', 'word', WORDS, 'enter',
      time=tw(400, stagger=120), props=dict(opacity=(0, 1), scale=(0.4, 1))),
    E('ScaleInText', 'Scale In Text', 'Scale & Zoom', 'the text springs up from half size', 'text',
      'SCALE IN TEXT', 'enter', time=spring(400, 25), props=dict(opacity=(0, 1), scale=(0.5, 1))),
    E('ZoomInText', 'Zoom In Text', 'Scale & Zoom', 'the text zooms in from the distance', 'text', 'ZOOM IN',
      'enter', time=tw(600, EXPO), weight=800, color='amber', props=dict(opacity=(0, 1), scale=(0.2, 1))),
    E('ZoomOutText', 'Zoom Out Text', 'Scale & Zoom', 'the text shrinks down into focus', 'text', 'ZOOM OUT',
      'enter', time=tw(600, EXPO), weight=800, color='amber', props=dict(opacity=(0, 1), scale=(1.8, 1))),
    # 3D & Rotate
    E('FlipYChar', 'Flip Y Char', '3D & Rotate', 'characters flip in around their vertical axis', 'char', CHAR,
      'enter', time=tw(500, stagger=50), color='indigo', props=dict(opacity=(0, 1), rotateY=(90, 0)),
      perspective=1000),
    E('FlipXChar', 'Flip X Char', '3D & Rotate', 'characters flip in around their horizontal axis', 'char', CHAR,
      'enter', time=tw(500, stagger=50), color='indigo', props=dict(opacity=(0, 1), rotateX=(90, 0)),
      perspective=1000),
    E('RotateInChar', 'Rotate In Char', '3D & Rotate', 'characters twist and grow into place', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), rotate=(-45, 0), scale=(0.5, 1))),
    E('SwingWord', 'Swing Word', '3D & Rotate', 'words swing down into place like a pendulum', 'word', WORDS,
      'enter', time=spring(350, 18, 120), color='purple', props=dict(opacity=(0, 1), rotateX=(-90, 0)),
      perspective=800),
    # Distortion & Spacing
    E('StretchXChar', 'Stretch X Char', 'Distortion & Spacing', 'characters squeeze in from wide', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), scaleX=(2.5, 1))),
    E('StretchYChar', 'Stretch Y Char', 'Distortion & Spacing', 'characters squeeze in from tall', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), scaleY=(2.5, 1))),
    E('SkewXChar', 'Skew X Char', 'Distortion & Spacing', 'characters straighten up from a slant', 'char', CHAR,
      'enter', time=tw(400, stagger=40), props=dict(opacity=(0, 1), skewX=(-30, 0))),
    E('TrackingInText', 'Tracking In Text', 'Distortion & Spacing', 'wide letter spacing tightens up', 'text',
      'TRACKING IN', 'enter', time=tw(700, EXPO), size=20, weight=900, unit='tracking', track=(0.6, 0.05)),
    E('TrackingOutText', 'Tracking Out Text', 'Distortion & Spacing', 'crushed letter spacing opens up', 'text',
      'TRACKING OUT', 'enter', time=tw(700, EXPO), size=20, weight=900, unit='tracking', track=(-0.2, 0.1)),
    # Hover & Interactive
    E('SpringText', 'Spring Text', 'Hover & Interactive', 'characters spring up and light up under the pointer',
      'char', CHAR, 'hover', hover=dict(k=500, c=15, y=-8, scale=1.2, color='0xFF6366F1')),
    E('HoverLiftChar', 'Hover Lift Char', 'Hover & Interactive', 'characters lift under the pointer', 'char',
      CHAR, 'hover', hover=dict(k=500, c=15, y=-8, scale=1.2, color='0xFF6366F1')),
    E('HoverLiftWord', 'Hover Lift Word', 'Hover & Interactive', 'words lift under the pointer', 'word', WORDS,
      'hover', hover=dict(k=400, c=18, y=-6, color='0xFF3B82F6')),
    E('HoverScaleChar', 'Hover Scale Char', 'Hover & Interactive', 'characters grow under the pointer', 'char',
      CHAR, 'hover', color='pink', hover=dict(k=500, c=18, scale=1.4)),
    E('HoverScaleWord', 'Hover Scale Word', 'Hover & Interactive', 'words grow under the pointer', 'word', WORDS,
      'hover', color='pink', hover=dict(k=400, c=20, scale=1.25)),
    # Continuous
    E('FloatChar', 'Float Char', 'Continuous', 'characters bob gently up and down', 'char', CHAR, 'loop',
      loop=(2000, 100), color='cyan', props=dict(y='_keyframes(const [0, -6, 0], u)')),
    E('FloatWord', 'Float Word', 'Continuous', 'words bob gently up and down', 'word', WORDS, 'loop',
      loop=(2400, 200), color='cyan', props=dict(y='_keyframes(const [0, -8, 0], u)')),
    E('PulseChar', 'Pulse Char', 'Continuous', 'characters breathe in and out of view', 'char', CHAR, 'loop',
      loop=(1500, 80), color='emerald', props=dict(opacity='_keyframes(const [0.3, 1, 0.3], u)')),
    E('PulseWord', 'Pulse Word', 'Continuous', 'words breathe in and out of view', 'word', WORDS, 'loop',
      loop=(1800, 250), color='emerald', props=dict(opacity='_keyframes(const [0.3, 1, 0.3], u)')),
    E('GlowText', 'Glow Text', 'Continuous', 'text with a softly breathing glow', 'text', 'GLOW TEXT', 'loop',
      loop=(2000, 0), size=30, weight=900, spacing=-0.025, color='indigoLight', unit='glow'),
]


def file_name(cls):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', '_', cls).lower()


def dart_num(v):
    if isinstance(v, str):
        return v
    if float(v).is_integer():
        return str(int(v))
    return repr(float(v))


def lerp(v, p='p'):
    """A pose value: a (from, to) pair or a raw Dart expression."""
    if isinstance(v, str):
        return v
    a, b = v
    return f'_lerp({dart_num(a)}, {dart_num(b)}, {p})'


# ---------------------------------------------------------------------------
# Pose code for one unit (a character, a word or the whole text).

def pose_body(e):
    props = e.get('props', {})
    unit = e.get('unit')
    lines = []
    if unit == 'wipe':
        lines.append('Widget child = Text(text, style: style, textAlign: TextAlign.center);')
    elif unit == 'typewriter':
        return '''return DecoratedBox(
  // The cursor is the right border, so it rides along the typed edge.
  decoration: BoxDecoration(border: Border(right: BorderSide(color: style.color ?? const Color(0xFF34D399), width: 2))),
  child: ClipRect(
    child: Align(
      alignment: Alignment.centerLeft,
      widthFactor: p.clamp(0.0, 1.0),
      child: Text(text, style: style, maxLines: 1, softWrap: false),
    ),
  ),
);'''
    elif unit == 'tracking':
        a, b = e['track']
        return f'''final size = style.fontSize ?? 20;
return Opacity(
  opacity: p.clamp(0.0, 1.0),
  child: Text(
    text,
    textAlign: TextAlign.center,
    style: style.copyWith(letterSpacing: _lerp({dart_num(a)}, {dart_num(b)}, p) * size),
  ),
);'''
    elif unit == 'shimmer':
        return '''// Tailwind's animate-pulse on a neutral-bright-neutral gradient.
return Opacity(
  opacity: _keyframes(const [1, 0.5, 1], u, const Cubic(0.4, 0, 0.6, 1)),
  child: ShaderMask(
    blendMode: BlendMode.srcIn,
    shaderCallback: (rect) => LinearGradient(colors: [edge, style.color!, edge]).createShader(rect),
    child: Text(text, style: style, textAlign: TextAlign.center),
  ),
);'''
    elif unit == 'glow':
        return '''// CSS text-shadow blurs of 10px → 25px (dark) or 20px (light), converted to Flutter's blurRadius.
final dark = Theme.of(context).brightness == Brightness.dark;
final glow = widget.glowColor ?? (dark ? const Color(0xFF6366F1) : const Color(0xFF4F46E5));
final alpha = dark ? const [0.5, 0.9, 0.5] : const [0.3, 0.6, 0.3];
final blur = dark ? const [7.8, 20.8, 7.8] : const [7.8, 16.5, 7.8];
return Text(
  text,
  textAlign: TextAlign.center,
  style: style.copyWith(
    shadows: [Shadow(color: glow.withValues(alpha: _keyframes(alpha, u)), blurRadius: _keyframes(blur, u))],
  ),
);'''
    else:
        lines.append('Widget child = Text(text, style: style);')

    blur = e.get('blur')
    if blur:
        lines.append(f'''final blur = _lerp({dart_num(blur)}, 0, p.clamp(0.0, 1.0));
child = ImageFiltered(
  enabled: blur > 0.01,
  imageFilter: ui.ImageFilter.blur(sigmaX: blur, sigmaY: blur, tileMode: TileMode.decal),
  child: child,
);''')
    if unit == 'wipe':
        lines.append('return ClipRect(clipper: _Wipe(p), child: child);')
        return '\n'.join(lines)

    if 'yFrac' in props:
        lines.append(f'child = FractionalTranslation(translation: Offset(0, {lerp(props["yFrac"])}), child: child);')

    ops = []
    if 'perspective' in e:
        ops.append(f'..setEntry(3, 2, -1 / {e["perspective"]})')
    if 'x' in props or 'y' in props:
        x = lerp(props['x']) if 'x' in props else '0'
        y = lerp(props['y']) if 'y' in props else '0'
        ops.append(f'..translateByDouble({x}, {y}, 0, 1)')
    for key, axis in (('rotate', 'Z'), ('rotateX', 'X'), ('rotateY', 'Y')):
        if key in props:
            ops.append(f'..rotate{axis}({lerp(props[key])} * math.pi / 180)')
    if 'scale' in props or 'scaleX' in props or 'scaleY' in props:
        if 'scale' in props:
            lines.append(f'final scale = {lerp(props["scale"])};')
            sx = sy = 'scale'
        else:
            sx = lerp(props['scaleX']) if 'scaleX' in props else '1'
            sy = lerp(props['scaleY']) if 'scaleY' in props else '1'
        ops.append(f'..scaleByDouble({sx}, {sy}, 1, 1)')
    if 'skewX' in props:
        ops.append(f'..multiply(Matrix4.skewX({lerp(props["skewX"])} * math.pi / 180))')
    if ops:
        chain = '\n    '.join(ops)
        lines.append(f'''child = Transform(
  alignment: Alignment.center,
  transform: Matrix4.identity()
    {chain},
  child: child,
);''')
    if 'opacity' in props:
        lines.append(f'child = Opacity(opacity: {lerp(props["opacity"])}.clamp(0.0, 1.0), child: child);')
    if e.get('clip') == 'unit':
        lines.append('child = ClipRect(child: child);')
    lines.append('return child;')
    return '\n'.join(lines)


def indent(s, n):
    pad = ' ' * n
    return '\n'.join(pad + l if l.strip() else '' for l in s.split('\n'))


# ---------------------------------------------------------------------------
# Shared pieces written into every file.

SPLIT = {
    'char': '''
/// Builds [text] one grapheme at a time (so emoji and Thai vowels stay whole),
/// keeping each word on one line and numbering units in reading order.
Widget _splitChars(String text, Widget Function(String unit, int index) unit) {
  final words = text.split(' ');
  final children = <Widget>[];
  var i = 0;
  for (var w = 0; w < words.length; w++) {
    final units = <Widget>[for (final c in words[w].characters) unit(c, i++)];
    // A non-breaking space, so the gap keeps its width at the end of a line.
    if (w < words.length - 1) units.add(unit('\\u00A0', i++));
    children.add(Row(mainAxisSize: MainAxisSize.min, children: units));
  }
  return Wrap(alignment: WrapAlignment.center, crossAxisAlignment: WrapCrossAlignment.center, children: children);
}
''',
    'word': '''
List<String> _words(String text) => [for (final w in text.split(' ')) if (w.isNotEmpty) w];

/// Builds [text] one word at a time with a gap of [gap] between words.
Widget _splitWords(String text, double gap, Widget Function(String unit, int index) unit) {
  final words = _words(text);
  return Wrap(
    alignment: WrapAlignment.center,
    crossAxisAlignment: WrapCrossAlignment.center,
    spacing: gap,
    children: [for (var i = 0; i < words.length; i++) unit(words[i], i)],
  );
}
''',
    'text': '',
}

COUNT = {
    'char': 'widget.text.characters.length',
    'word': '_words(widget.text).length',
    'text': '1',
}


def layout_call(mode, clip_all=False):
    if mode == 'char':
        s = '_splitChars(widget.text, (text, i) => _unit(context, text, style, time, i))'
    elif mode == 'word':
        s = '_splitWords(widget.text, (style.fontSize ?? 20) * 0.4, (text, i) => _unit(context, text, style, time, i))'
    else:
        s = '_unit(context, widget.text, style, time, 0)'
    return f'ClipRect(child: {s})' if clip_all else s


KEYFRAMES = '''
/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t, [Curve curve = Curves.easeInOut]) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = math.min(x.floor(), segments - 1);
  return values[i] + (values[i + 1] - values[i]) * curve.transform(x - i);
}
'''

LERP = '''
double _lerp(double a, double b, double t) => a + (b - a) * t;
'''

WIPE = '''
/// Shows the left [p] of the child, like `clip-path: inset(0 100% 0 0)` → `inset(0)`.
class _Wipe extends CustomClipper<Rect> {
  _Wipe(this.p);

  final double p;

  @override
  Rect getClip(Size size) => Rect.fromLTWH(0, 0, size.width * p.clamp(0.0, 1.0), size.height);

  @override
  bool shouldReclip(_Wipe oldClipper) => oldClipper.p != p;
}
'''


def style_code(e):
    dark, light = COLORS[e.get('color', 'plain')]
    size = e.get('size', 24 if e['mode'] != 'word' else 20)
    weight = e.get('weight', 700)
    extra = ''
    if 'spacing' in e:
        extra = f', letterSpacing: {dart_num(e["spacing"])} * {size}'
    if e.get('unit') == 'typewriter':
        extra += ", fontFamily: 'monospace'"
    return f'''final dark = Theme.of(context).brightness == Brightness.dark;
var style = DefaultTextStyle.of(context).style
    .merge(TextStyle(fontSize: {size}, fontWeight: FontWeight.w{weight}, color: dark ? {dark} : {light}{extra}))
    .merge(widget.style);
if (widget.color != null) style = style.copyWith(color: widget.color);'''


def usage(e):
    s = e['sample']
    cls = e['cls']
    lines = [f"//   const {cls}('{s}')"]
    if e['kind'] == 'enter':
        if e['mode'] == 'text':
            lines.append(f"//   {cls}('Hello world', style: TextStyle(fontSize: 48), delay: Duration(milliseconds: 300))")
        else:
            lines.append(f"//   {cls}('Hello world', style: TextStyle(fontSize: 48), stagger: Duration(milliseconds: 80))")
        lines.append('//')
        lines.append('// Plays once when first shown, and again whenever `text` changes. Give it a new')
        lines.append('// Key to replay it. With reduced motion turned on, it shows the final state.')
    elif e['kind'] == 'loop':
        lines.append(f"//   {cls}('Hello world', color: Colors.teal)")
    else:
        lines.append(f"//   {cls}('Hello world', style: TextStyle(fontSize: 48))")
        lines.append('//')
        lines.append('// Reacts to a mouse pointer; on touch screens the text simply stays still.')
    return '\n'.join(lines)


def header(e):
    color = COLOR_NAMES[e.get('color', 'plain')]
    sentence = e['desc'][0].upper() + e['desc'][1:]
    return f'''// {e['cls']} — {e['desc']}.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's "{e['label']}" text animation (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
{usage(e)}
''', sentence, color


def imports(code):
    out = []
    if 'math.' in code:
        out.append("import 'dart:math' as math;")
    if 'ui.ImageFilter' in code:
        out.append("import 'dart:ui' as ui;")
    if out:
        out.append('')
    out.append("import 'package:flutter/material.dart';")
    if 'SpringSimulation(' in code:
        out.append("import 'package:flutter/physics.dart';")
    if 'Ticker ' in code:
        out.append("import 'package:flutter/scheduler.dart';")
    return '\n'.join(out)


def timed_widget(e):
    cls, mode, kind = e['cls'], e['mode'], e['kind']
    head, sentence, color = header(e)
    params, fields, extra_state = [], [], []

    params.append('this.style')
    fields.append('''  /// Merged over the default style.
  final TextStyle? style;''')
    params.append('this.color')
    fields.append(f'''  /// Defaults to {color} for the current light/dark theme.
  final Color? color;''')

    if kind == 'enter':
        typ, a, b, stagger = e['time']
        params.append('this.delay = Duration.zero')
        fields.append('''  /// Wait before the animation starts.
  final Duration delay;''')
        if typ == 'tween':
            params.append(f'this.duration = const Duration(milliseconds: {a})')
            per = ' of each character' if mode == 'char' else (' of each word' if mode == 'word' else '')
            fields.append(f'''  /// Length of the animation{per}.
  final Duration duration;''')
        if mode != 'text':
            params.append(f'this.stagger = const Duration(milliseconds: {stagger})')
            fields.append(f'''  /// Time between one {'character' if mode == 'char' else 'word'} starting and the next.
  final Duration stagger;''')
    else:
        ms, offset = e['loop']
        params.append(f'this.duration = const Duration(milliseconds: {ms})')
        fields.append('''  /// Length of one loop.
  final Duration duration;''')
        if mode != 'text':
            params.append(f'this.stagger = const Duration(milliseconds: {offset})')
            fields.append(f'''  /// How far each {'character' if mode == 'char' else 'word'} runs behind the one before it.
  final Duration stagger;''')
    if e.get('unit') == 'glow':
        params.append('this.glowColor')
        fields.append('''  /// Colour of the glow; defaults to indigo.
  final Color? glowColor;''')

    ctor_params = ''.join(f'\n    {p},' for p in params)
    field_block = '\n\n'.join(fields)

    # Progress helpers.
    if kind == 'enter':
        typ, a, b, stagger = e['time']
        stagger_s = '_seconds(widget.stagger)' if mode != 'text' else '0'
        if typ == 'tween':
            unit_len = '_seconds(widget.duration)'
            progress = f'''  /// Linear progress (0..1) of unit [i] at [time] seconds.
  double _linear(double time, int i) {{
    final length = _seconds(widget.duration);
    if (length <= 0) return 1;
    return ((time - i * {stagger_s}) / length).clamp(0.0, 1.0);
  }}'''
            unit_head = f'''    final t = _linear(time, i);
    final p = {'' if b.startswith('Curves.') else 'const '}{b}.transform(t);'''
            spring_field = ''
        else:
            unit_len = f'{16 / b:.3f}'
            progress = f'''  // Spring(stiffness: {a}, damping: {b}); it has settled after {16 / b:.3f}s.
  static final _spring = SpringSimulation(const SpringDescription(mass: 1, stiffness: {a}, damping: {b}), 0, 1, 0);

  double _sprung(double time, int i) {{
    final local = time - i * {stagger_s};
    if (local <= 0) return 0;
    if (local >= {16 / b:.3f}) return 1;
    return _spring.x(local);
  }}'''
            unit_head = '    final p = _sprung(time, i);'
            spring_field = ''
        end = f'  double get _end => math.max(0, {COUNT[mode]} - 1) * {stagger_s} + {unit_len};'
        tick = '''  void _onTick(Duration elapsed) {
    _time.value = elapsed.inMicroseconds / 1e6 - _seconds(widget.delay);
    if (_time.value >= _end) _ticker.stop();
  }

  @override
  void didUpdateWidget(covariant CLS oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text != widget.text) {
      _ticker.stop();
      _time.value = -_seconds(widget.delay);
      _ticker.start();
    }
  }'''.replace('CLS', cls)
        time_line = '''    // With reduced motion, jump straight to the end.
    final still = MediaQuery.maybeDisableAnimationsOf(context) ?? false;'''
        builder_time = 'still ? double.infinity : t'
        init_time = '-_seconds(widget.delay)'
    else:
        ms, offset = e['loop']
        spring_field = ''
        stagger_s = '_seconds(widget.stagger)' if mode != 'text' else '0'
        progress = f'''  /// Position (0..1) in the loop of unit [i]; each unit starts {'[stagger] after the one before' if mode != 'text' else 'at once'}.
  double _loop(double time, int i) {{
    final local = time - i * {stagger_s};
    final length = _seconds(widget.duration);
    if (local <= 0 || length <= 0) return 0;
    return local / length % 1.0;
  }}'''
        unit_head = '    final u = _loop(time, i);'
        end = ''
        tick = '''  void _onTick(Duration elapsed) => _time.value = elapsed.inMicroseconds / 1e6;'''
        time_line = ''
        builder_time = 't'
        init_time = '0'

    end_block = '\n' + end + '\n' if end else ''
    body = pose_body(e)
    if e.get('unit') == 'shimmer':
        unit_head += '''
    final dark = Theme.of(context).brightness == Brightness.dark;
    final edge = widget.color?.withValues(alpha: 0.6) ?? (dark ? const Color(0xFFA3A3A3) : const Color(0xFF525252));'''

    layout = layout_call(mode, e.get('clip') == 'all')
    style = style_code(e)

    code = f'''{head}
IMPORTS

class {cls} extends StatefulWidget {{
  const {cls}(this.text, {{super.key,{ctor_params}
  }});

  final String text;

{field_block}

  @override
  State<{cls}> createState() => _{cls}State();
}}

class _{cls}State extends State<{cls}> with SingleTickerProviderStateMixin {{
  late final Ticker _ticker = createTicker(_onTick);
  // Seconds since the animation started (negative while waiting for the delay).
  late final _time = ValueNotifier<double>({init_time});

  @override
  void initState() {{
    super.initState();
    _ticker.start();
  }}

{tick}

  @override
  void dispose() {{
    _ticker.dispose();
    _time.dispose();
    super.dispose();
  }}
{end_block}
{progress}

  @override
  Widget build(BuildContext context) {{
{indent(style, 4)}
{time_line}
    return Semantics(
      label: widget.text,
      child: ExcludeSemantics(
        child: RepaintBoundary(
          child: ValueListenableBuilder<double>(
            valueListenable: _time,
            builder: (context, t, _) {{
              final time = {builder_time};
              return {layout};
            }},
          ),
        ),
      ),
    );
  }}

  /// One {'character' if mode == 'char' else 'word' if mode == 'word' else 'copy of the text'} at [time] seconds.
  Widget _unit(BuildContext context, String text, TextStyle style, double time, int i) {{
{unit_head}
{indent(body, 4)}
  }}
}}

double _seconds(Duration d) => d.inMicroseconds / 1e6;
'''
    if '_lerp(' in code:
        code += LERP
    if '_keyframes(' in code:
        code += KEYFRAMES
    code += SPLIT[mode]
    if '_Wipe(' in code:
        code += WIPE
    return finish(code)


def hover_widget(e):
    cls, mode = e['cls'], e['mode']
    head, sentence, color = header(e)
    h = e['hover']
    has_color = 'color' in h
    params = ['this.style', 'this.color']
    fields = ['''  /// Merged over the default style.
  final TextStyle? style;''', f'''  /// Defaults to {color} for the current light/dark theme.
  final Color? color;''']
    if has_color:
        params.append(f'this.hoverColor = const Color({h["color"]})')
        fields.append('''  /// Colour a unit turns while the pointer is over it.
  final Color hoverColor;''')
    ctor_params = ''.join(f'\n    {p},' for p in params)
    field_block = '\n\n'.join(fields)

    ops = []
    if 'y' in h:
        ops.append(f'..translateByDouble(0, {dart_num(h["y"])} * v, 0, 1)')
    if 'scale' in h:
        ops.append(f'..scaleByDouble(1 + {dart_num(round(h["scale"] - 1, 4))} * v, 1 + {dart_num(round(h["scale"] - 1, 4))} * v, 1, 1)')
    chain = '\n            '.join(ops)
    text_style = ('widget.style.copyWith(color: Color.lerp(widget.style.color, widget.hoverColor, v.clamp(0.0, 1.0)))'
                  if has_color else 'widget.style')

    split = ('_splitChars(text, (unit, _) => _HoverUnit(text: unit, style: style' if mode == 'char'
             else '_splitWords(text, (style.fontSize ?? 20) * 0.4, (unit, _) => _HoverUnit(text: unit, style: style')
    split += ', hoverColor: hoverColor))' if has_color else '))'
    unit_fields = '''  final String text;
  final TextStyle style;''' + ('\n  final Color hoverColor;' if has_color else '')
    unit_ctor = 'required this.text, required this.style' + (', required this.hoverColor' if has_color else '')

    code = f'''{head}
IMPORTS

class {cls} extends StatelessWidget {{
  const {cls}(this.text, {{super.key,{ctor_params}
  }});

  final String text;

{field_block}

  @override
  Widget build(BuildContext context) {{
{indent(style_code(e).replace('widget.style', 'this.style').replace('widget.color', 'color'), 4)}
    return Semantics(label: text, child: ExcludeSemantics(child: {split}));
  }}
}}

/// One {'character' if mode == 'char' else 'word'} that springs towards its hover pose.
class _HoverUnit extends StatefulWidget {{
  const _HoverUnit({{{unit_ctor}}});

{unit_fields}

  @override
  State<_HoverUnit> createState() => _HoverUnitState();
}}

class _HoverUnitState extends State<_HoverUnit> with SingleTickerProviderStateMixin {{
  // 0 = resting, 1 = hovered; the spring may overshoot a little.
  late final AnimationController _hover = AnimationController.unbounded(vsync: this);

  static const _spring = SpringDescription(mass: 1, stiffness: {h['k']}, damping: {h['c']});

  void _to(double target) {{
    _hover
        .animateWith(SpringSimulation(_spring, _hover.value, target, _hover.velocity))
        // The spring stops within a hair of its target; land exactly on it.
        .whenComplete(() => _hover.value = target);
  }}

  @override
  void dispose() {{
    _hover.dispose();
    super.dispose();
  }}

  @override
  Widget build(BuildContext context) {{
    return MouseRegion(
      onEnter: (_) => _to(1),
      onExit: (_) => _to(0),
      child: AnimatedBuilder(
        animation: _hover,
        builder: (context, _) {{
          final v = _hover.value;
          return Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
            {chain},
            child: Text(widget.text, style: {text_style}),
          );
        }},
      ),
    );
  }}
}}
'''
    code += SPLIT[mode]
    return finish(code)


def finish(code):
    code = code.replace('IMPORTS', imports(code))
    code = re.sub(r'\n{3,}', '\n\n', code)
    return code


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        if old.endswith('.dart'):
            os.remove(os.path.join(OUT, old))
    for e in EFFECTS:
        code = hover_widget(e) if e['kind'] == 'hover' else timed_widget(e)
        with open(os.path.join(OUT, file_name(e['cls']) + '.dart'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(code)

    # Gallery catalogue.
    with open(os.path.join(ROOT, 'example', 'lib', 'text_catalog.g.dart'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_text.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('typedef TextEntry = ({String name, String category, String source, WidgetBuilder builder});\n\n')
        fh.write('final List<TextEntry> textCatalog = [\n')
        for e in EFFECTS:
            if 'gallery_style' in e:
                build = f"{e['cls']}({e['sample']!r}, style: const TextStyle({e['gallery_style']}))"
            else:
                build = f"const {e['cls']}({e['sample']!r})"
            fh.write(f"  (name: {e['label']!r}, category: {e['cat']!r}, "
                     f"source: 'text/{file_name(e['cls'])}.dart', builder: (_) => {build}),\n")
        fh.write('];\n')

    # Test table: every widget with its kind and how its text is split.
    with open(os.path.join(ROOT, 'test', 'text_widgets.g.dart'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_text.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('enum TextKind { enter, loop, hover }\n\n')
        fh.write('enum TextSplit { char, word, text }\n\n')
        fh.write('final textWidgets = <String, (TextKind, TextSplit, Widget Function(String text))>{\n')
        for e in EFFECTS:
            fh.write(f"  '{e['cls']}': (TextKind.{e['kind']}, TextSplit.{e['mode']}, (s) => {e['cls']}(s)),\n")
        fh.write('};\n')

    # Library exports: keep everything else, then list the text widgets.
    lib = os.path.join(ROOT, 'lib', 'flutter_motion_kit.dart')
    s = open(lib, encoding='utf-8').read()
    s = re.sub(r"export 'widgets/text/[^']+';\n", '', s).rstrip('\n') + '\n'
    s += ''.join(f"export 'widgets/text/{file_name(e['cls'])}.dart';\n" for e in EFFECTS)
    with open(lib, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)
    subprocess.run('dart format lib/widgets/text lib/flutter_motion_kit.dart test/text_widgets.g.dart '
                   'example/lib/text_catalog.g.dart', shell=True, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    print(f'Generated {len(EFFECTS)} text animations')


if __name__ == '__main__':
    main()
