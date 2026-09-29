# Generates lib/widgets/loaders/*.dart plus the gallery catalogue and exports.
#
# Each loader file must stand alone (copy-paste rule), so the shared boilerplate
# (controller, theme colour, keyframe helpers) is written into every file rather
# than imported. Edit a loader's `body` here, then run:
#
#   python tool/gen_loaders.py
import os
import re
import textwrap

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'lib', 'widgets', 'loaders')

DEFAULT_COLOR = 'dark ? Colors.white : const Color(0xFF27272A)'
TRACK = 'final track = dark ? const Color(0xFF27272A) : const Color(0xFFE4E4E7);'

HELPERS = {
    'phase': '''
/// Position in the loop for an element that starts [shift] (0..1 of a loop) late.
double _phase(double t, double shift) => (t - shift) % 1.0;
''',
    'keyframes': '''
/// Evenly spaced keyframes, eased per segment (like Motion's `animate: [a, b, c]`).
double _keyframes(List<double> values, double t, [Curve curve = Curves.easeInOut]) {
  final segments = values.length - 1;
  final x = t.clamp(0.0, 1.0) * segments;
  final i = math.min(x.floor(), segments - 1);
  return values[i] + (values[i + 1] - values[i]) * curve.transform(x - i);
}
''',
    'dot': '''
Widget _dot(double size, Color color) => Container(
      width: size,
      height: size,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
''',
}

LOADERS = [
    dict(cls='PulseDots', file='pulse_dots', ms=1400, cat='Dots', desc='three dots fading in and out in turn', body='''
return Row(mainAxisSize: MainAxisSize.min, children: [
  for (var i = 0; i < 3; i++)
    Padding(
      padding: EdgeInsets.only(left: i == 0 ? 0 : 6),
      child: Opacity(opacity: _keyframes(const [0.2, 1, 0.2], _phase(t, i * 0.2 / 1.4)), child: _dot(10, color)),
    ),
]);'''),
    dict(cls='BounceDots', file='bounce_dots', ms=600, cat='Dots', desc='three dots hopping one after another', body='''
return SizedBox(
  height: 18,
  child: Row(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.end, children: [
    for (var i = 0; i < 3; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 6),
        child: Transform.translate(
          offset: Offset(0, _keyframes(const [0, -8, 0], _phase(t, i * 0.1 / 0.6))),
          child: _dot(10, color),
        ),
      ),
  ]),
);'''),
    dict(cls='WaveDots', file='wave_dots', ms=1000, cat='Dots', desc='five dots rolling in a wave', body='''
return SizedBox(
  height: 24,
  child: Row(mainAxisSize: MainAxisSize.min, children: [
    for (var i = 0; i < 5; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 6),
        child: Transform.translate(
          offset: Offset(0, _keyframes(const [4, -4, 4], _phase(t, i * 0.15))),
          child: _dot(8, color),
        ),
      ),
  ]),
);'''),
    dict(cls='GridDots', file='grid_dots', ms=1500, cat='Dots', desc='a 3x3 grid pulsing diagonally', body='''
return Column(mainAxisSize: MainAxisSize.min, children: [
  for (var row = 0; row < 3; row++)
    Padding(
      padding: EdgeInsets.only(top: row == 0 ? 0 : 6),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        for (var col = 0; col < 3; col++)
          Padding(
            padding: EdgeInsets.only(left: col == 0 ? 0 : 6),
            child: Opacity(
              opacity: _keyframes(const [1, 0.3, 1], _phase(t, (row + col) * 0.2 / 1.5)),
              child: Transform.scale(
                scale: _keyframes(const [1, 0.5, 1], _phase(t, (row + col) * 0.2 / 1.5)),
                child: _dot(10, color),
              ),
            ),
          ),
      ]),
    ),
]);'''),
    dict(cls='TypingIndicator', file='typing_indicator', ms=600, cat='Dots', desc='a chat bubble with three bobbing dots',
         color='dark ? const Color(0xFFA1A1AA) : const Color(0xFF71717A)', body='''
return Container(
  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
  decoration: BoxDecoration(
    color: dark ? const Color(0xFF27272A) : const Color(0xFFF4F4F5),
    borderRadius: BorderRadius.circular(999),
  ),
  child: Row(mainAxisSize: MainAxisSize.min, children: [
    for (var i = 0; i < 3; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 4),
        child: Transform.translate(
          offset: Offset(0, _keyframes(const [0, -4, 0], _phase(t, i * 0.15 / 0.6))),
          child: _dot(6, color),
        ),
      ),
  ]),
);'''),
    dict(cls='DotsRing', file='dots_ring', ms=1500, cat='Dots', desc='eight dots in a circle pulsing around', body='''
return SizedBox.square(
  dimension: 48,
  child: Stack(children: [
    for (var i = 0; i < 8; i++)
      Positioned(
        left: 24 + 20 * math.sin(i * math.pi / 4) - 4,
        top: 24 - 20 * math.cos(i * math.pi / 4) - 4,
        child: Opacity(
          opacity: _keyframes(const [1, 0.3, 1], _phase(t, i * 0.15 / 1.5)),
          child: Transform.scale(
            scale: _keyframes(const [1, 0.5, 1], _phase(t, i * 0.15 / 1.5)),
            child: _dot(8, color),
          ),
        ),
      ),
  ]),
);'''),
    dict(cls='ClassicSpinner', file='classic_spinner', ms=1000, cat='Rings',
         desc='twelve fading spokes, the classic activity spinner',
         color='dark ? const Color(0xFFE4E4E7) : const Color(0xFFA1A1AA)', body='''
return SizedBox.square(
  dimension: 32,
  child: Stack(children: [
    for (var i = 0; i < 12; i++)
      Positioned.fill(
        child: Transform.rotate(
          angle: i * math.pi / 6,
          child: Align(
            alignment: Alignment.topCenter,
            child: Opacity(
              opacity: _keyframes(const [1, 0.2], _phase(t, i / 12), Curves.linear),
              child: Container(
                width: 4,
                height: 8,
                decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
              ),
            ),
          ),
        ),
      ),
  ]),
);'''),
    dict(cls='IOSSpinner', name='iOS Spinner', file='ios_spinner', ms=1000, cat='Rings', desc='the thin twelve-spoke iOS activity indicator', body='''
return SizedBox.square(
  dimension: 32,
  child: Stack(children: [
    for (var i = 0; i < 12; i++)
      Positioned.fill(
        child: Transform.rotate(
          angle: i * math.pi / 6,
          child: Align(
            alignment: Alignment.topCenter,
            child: Opacity(
              opacity: _keyframes(const [1, 0.2], _phase(t, i / 12), Curves.linear),
              child: Container(
                width: 2,
                height: 7,
                decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(1)),
              ),
            ),
          ),
        ),
      ),
  ]),
);'''),
    dict(cls='CometSpinner', file='comet_spinner', ms=1000, cat='Rings', desc='a ring with a comet tail sweeping around',
         extra_state=TRACK, body='''
return SizedBox.square(
  dimension: 40,
  child: CustomPaint(painter: _CometPainter(t, color, track)),
);''', tail='''
class _CometPainter extends CustomPainter {
  _CometPainter(this.t, this.color, this.track);

  final double t;
  final Color color;
  final Color track;

  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero);
    final r = size.width / 2 - 2;
    canvas.drawCircle(
      c,
      size.width / 2 - 0.5,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = track,
    );
    final sweep = SweepGradient(
      colors: [color.withValues(alpha: 0), color.withValues(alpha: 0.1), color],
      stops: const [0, 0.6, 1],
      transform: GradientRotation(t * 2 * math.pi - math.pi / 2),
    );
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..shader = sweep.createShader(Rect.fromCircle(center: c, radius: r)),
    );
  }

  @override
  bool shouldRepaint(_CometPainter old) => old.t != t || old.color != color || old.track != track;
}
'''),
    dict(cls='ArcTracer', file='arc_tracer', ms=2000, cat='Rings',
         desc='an arc that draws itself around a track, then chases its tail away', extra_state=TRACK, body='''
return SizedBox.square(
  dimension: 40,
  child: CustomPaint(painter: _ArcTracerPainter(_keyframes(const [125, 0, -125], t), color, track)),
);''', tail='''
class _ArcTracerPainter extends CustomPainter {
  _ArcTracerPainter(this.offset, this.color, this.track);

  /// SVG-style dash offset on a 125-long dash (the circle's circumference is ~125.7).
  final double offset;
  final Color color;
  final Color track;

  static const _circumference = 2 * math.pi * 20;

  @override
  void paint(Canvas canvas, Size size) {
    final scale = size.width / 50;
    final rect = Rect.fromCircle(center: size.center(Offset.zero), radius: 20 * scale);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4 * scale
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, 0, 2 * math.pi, false, stroke..color = track);

    final start = math.max(0.0, -offset);
    final end = math.min(_circumference, 125 - offset);
    if (end - start < 0.5) return;
    canvas.drawArc(
      rect,
      start / _circumference * 2 * math.pi,
      (end - start) / _circumference * 2 * math.pi,
      false,
      stroke..color = color,
    );
  }

  @override
  bool shouldRepaint(_ArcTracerPainter old) => old.offset != offset || old.color != color || old.track != track;
}
'''),
    dict(cls='DualArc', file='dual_arc', ms=1200, cat='Rings', desc='two opposite arcs spinning and breathing', body='''
return SizedBox.square(
  dimension: 32,
  child: Transform.rotate(
    angle: t * 2 * math.pi,
    child: Transform.scale(
      scale: _keyframes(const [1, 0.82, 1], t),
      child: CustomPaint(painter: _DualArcPainter(color)),
    ),
  ),
);''', tail='''
class _DualArcPainter extends CustomPainter {
  _DualArcPainter(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(1);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = color;
    // Top and bottom quarters, like a circle with only border-top and border-bottom.
    canvas.drawArc(rect, -3 * math.pi / 4, math.pi / 2, false, paint);
    canvas.drawArc(rect, math.pi / 4, math.pi / 2, false, paint);
  }

  @override
  bool shouldRepaint(_DualArcPainter old) => old.color != color;
}
'''),
    dict(cls='OrbitingDot', file='orbiting_dot', ms=2000, cat='Rings', desc='a dot orbiting a faint ring',
         extra_state=TRACK, body='''
return SizedBox.square(
  dimension: 40,
  child: Stack(alignment: Alignment.center, clipBehavior: Clip.none, children: [
    _dot(8, dark ? const Color(0xFF3F3F46) : const Color(0xFFD4D4D8)),
    Transform.rotate(
      angle: t * 2 * math.pi,
      child: Stack(clipBehavior: Clip.none, children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: track)),
        ),
        Positioned(left: 14, top: -6, child: _dot(12, color)),
      ]),
    ),
  ]),
);'''),
    dict(cls='RippleEffect', file='ripple_effect', ms=2200, cat='Rings', desc='rings rippling out from a centre dot', body='''
return SizedBox.square(
  dimension: 48,
  child: Stack(alignment: Alignment.center, clipBehavior: Clip.none, children: [
    _dot(10, color),
    for (var i = 0; i < 3; i++)
      Opacity(
        opacity: 0.8 * (1 - Curves.easeOut.transform(_phase(t, i * 0.7 / 2.2))),
        child: Transform.scale(
          scale: 0.3 + 1.3 * Curves.easeOut.transform(_phase(t, i * 0.7 / 2.2)),
          child: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: color)),
          ),
        ),
      ),
  ]),
);'''),
    dict(cls='BouncingBars', file='bouncing_bars', ms=1000, cat='Bars', desc='three bars stretching up and down in turn', body='''
return SizedBox(
  height: 32,
  child: Row(mainAxisSize: MainAxisSize.min, children: [
    for (var i = 0; i < 3; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 6),
        child: Transform(
          alignment: Alignment.center,
          transform: Matrix4.diagonal3Values(1, _keyframes(const [0.3, 1, 0.3], _phase(t, i * 0.2)), 1),
          child: Container(
            width: 6,
            height: 32,
            decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3)),
          ),
        ),
      ),
  ]),
);'''),
    dict(cls='BarCascade', file='bar_cascade', ms=1000, cat='Bars', desc='five bars growing in a cascade', body='''
return SizedBox(
  height: 32,
  child: Row(mainAxisSize: MainAxisSize.min, children: [
    for (var i = 0; i < 5; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 4),
        child: Container(
          width: 6,
          height: _keyframes(const [8, 24, 8], _phase(t, i * 0.1)),
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3)),
        ),
      ),
  ]),
);'''),
    dict(cls='Equalizer', file='equalizer', ms=800, cat='Bars', desc='four equalizer bars bouncing to the beat', body='''
// Fixed offsets so it looks organic but renders the same every time.
const shifts = [0.0, 0.375, 0.1875, 0.5625];
return SizedBox(
  height: 32,
  child: Row(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.end, children: [
    for (var i = 0; i < 4; i++)
      Padding(
        padding: EdgeInsets.only(left: i == 0 ? 0 : 4),
        child: Container(
          width: 6,
          height: 32 * _keyframes(const [0.2, 1, 0.2], _phase(t, shifts[i]), Curves.easeInOutCirc),
          decoration: BoxDecoration(color: color, borderRadius: const BorderRadius.vertical(top: Radius.circular(2))),
        ),
      ),
  ]),
);'''),
    dict(cls='FlipSquare', file='flip_square', ms=2000, cat='Shapes',
         desc='a square flipping over on one axis, then the other', body='''
return Transform(
  alignment: Alignment.center,
  transform: Matrix4.identity()
    ..setEntry(3, 2, 0.002)
    ..rotateX(_keyframes(const [0, 180, 180, 0], t) * math.pi / 180)
    ..rotateY(_keyframes(const [0, 0, 180, 180], t) * math.pi / 180),
  child: Container(
    width: 32,
    height: 32,
    decoration: BoxDecoration(
      color: color,
      borderRadius: BorderRadius.circular(6),
      boxShadow: const [BoxShadow(color: Color(0x14000000), blurRadius: 2, offset: Offset(0, 1))],
    ),
  ),
);'''),
    dict(cls='NewtonsCradle', name="Newton's Cradle", file='newtons_cradle', ms=1500, cat='Shapes',
         desc="four balls clacking like a Newton's cradle", body='''
Widget swing(double degrees) => Transform(
      alignment: Alignment.topCenter,
      // Pivot on an invisible string above the ball so it swings in an arc.
      origin: const Offset(0, -20),
      transform: Matrix4.rotationZ(degrees * math.pi / 180),
      child: _dot(12, color),
    );
return Padding(
  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
  child: Row(mainAxisSize: MainAxisSize.min, children: [
    swing(_keyframes(const [25, 0, 0, 0, 0, 25], t)),
    const SizedBox(width: 2),
    _dot(12, color),
    const SizedBox(width: 2),
    _dot(12, color),
    const SizedBox(width: 2),
    swing(_keyframes(const [0, 0, 0, -25, 0, 0], t)),
  ]),
);'''),
    dict(cls='SquareSpinner', file='square_spinner', ms=600, cat='Shapes',
         desc='a square outline ticking round a quarter turn at a time', body='''
return Transform.rotate(
  angle: Curves.easeInOut.transform(t) * math.pi / 2,
  child: Container(
    width: 32,
    height: 32,
    alignment: Alignment.center,
    decoration: BoxDecoration(border: Border.all(color: dark ? const Color(0xFF3F3F46) : color, width: 2)),
    child: Container(width: 8, height: 8, color: color),
  ),
);'''),
    dict(cls='TextShimmer', file='text_shimmer', ms=1500, cat='Text', desc='text with a shine sweeping across it',
         params=[('String', 'text', "'Thinking'", 'The text to shimmer.')], body='''
final style = TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: color);
return Stack(children: [
  Text(widget.text, style: style.copyWith(color: color.withValues(alpha: 0.25))),
  ShaderMask(
    blendMode: BlendMode.dstIn,
    shaderCallback: (rect) {
      // A band twice as wide as the text slides left to right; its opaque middle is the shine.
      final w = rect.width;
      return const LinearGradient(
        colors: [Color(0x00000000), Color(0xFF000000), Color(0x00000000)],
      ).createShader(Rect.fromLTWH(-w + 2 * w * t, 0, 2 * w, rect.height));
    },
    child: Text(widget.text, style: style),
  ),
]);'''),
]

TEMPLATE = '''// {cls} — {desc}.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
//   const {cls}()
//   {cls}(color: Colors.teal)

import 'dart:math' as math;

import 'package:flutter/material.dart';

class {cls} extends StatefulWidget {{
  const {cls}({{super.key, this.color, this.duration = const Duration(milliseconds: {ms}){ctor_extra}}});

  /// Defaults to a neutral that suits the current light/dark theme.
  final Color? color;

  /// Length of one loop.
  final Duration duration;
{fields}
  @override
  State<{cls}> createState() => _{cls}State();
}}

class _{cls}State extends State<{cls}> with SingleTickerProviderStateMixin {{
  late final AnimationController _controller = AnimationController(vsync: this, duration: widget.duration)
    ..repeat();

  @override
  void didUpdateWidget({cls} oldWidget) {{
    super.didUpdateWidget(oldWidget);
    if (oldWidget.duration != widget.duration) {{
      _controller
        ..duration = widget.duration
        ..repeat();
    }}
  }}

  @override
  void dispose() {{
    _controller.dispose();
    super.dispose();
  }}

  @override
  Widget build(BuildContext context) {{
    final dark = Theme.of(context).brightness == Brightness.dark;
    final color = widget.color ?? ({color});
{extra_state}    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {{
          final t = _controller.value;
{body}
        }},
      ),
    );
  }}
}}
{helpers}{tail}'''


def indent(s, n):
    return textwrap.indent(s.strip('\n'), ' ' * n)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.dart'):
            os.remove(os.path.join(OUT, f))

    for L in LOADERS:
        body, tail = L['body'], L.get('tail', '')
        code = body + tail
        helpers = ''.join(h for k, h in HELPERS.items() if re.search(r'\b_' + k + r'\(', code))
        params = L.get('params', [])
        ctor_extra = ''.join(f', this.{n} = {d}' for _, n, d, _ in params)
        fields = ''.join(f'\n  /// {doc}\n  final {ty} {n};\n' for ty, n, d, doc in params)
        src = TEMPLATE.format(
            cls=L['cls'], desc=L['desc'], ms=L['ms'], ctor_extra=ctor_extra, fields=fields,
            color=L.get('color', DEFAULT_COLOR),
            extra_state=indent(L['extra_state'], 4) + '\n' if L.get('extra_state') else '',
            body=indent(body, 10), helpers=helpers, tail=tail)
        after_imports = src.split("import 'package:flutter/material.dart';", 1)[1]
        if 'math.' not in after_imports:
            src = src.replace("import 'dart:math' as math;\n\n", '')
        with open(os.path.join(OUT, L['file'] + '.dart'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(src)

    # Gallery catalogue.
    cat = os.path.join(ROOT, 'example', 'lib', 'loader_catalog.g.dart')
    with open(cat, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_loaders.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('typedef LoaderEntry = ({String name, String category, String source, WidgetBuilder builder});\n\n')
        fh.write('final List<LoaderEntry> loaderCatalog = [\n')
        for L in LOADERS:
            name = L.get('name') or re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', L['cls'])
            fh.write(f"  (name: {name!r}, category: '{L['cat']}', source: 'loaders/{L['file']}.dart', "
                     f"builder: (_) => const {L['cls']}()),\n")
        fh.write('];\n')

    # Library exports: keep everything that isn't a loader, then list loaders.
    lib = os.path.join(ROOT, 'lib', 'flutter_motion_kit.dart')
    s = open(lib, encoding='utf-8').read()
    s = re.sub(r"export 'widgets/loaders/[^']+';\n", '', s).rstrip('\n') + '\n'
    s += ''.join(f"export 'widgets/loaders/{L['file']}.dart';\n" for L in LOADERS)
    with open(lib, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)
    print(f'Generated {len(LOADERS)} loaders')


if __name__ == '__main__':
    main()
