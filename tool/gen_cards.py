# Generates the hover card layouts in lib/widgets/cards/ (ports of Amicro's card
# layouts). They all share one mechanism: on hover every card springs from a resting
# pose to a spread pose. Each file must stand alone (copy-paste rule), so that
# mechanism is written into every file rather than imported.
#
# Edit a layout here, then run:  python tool/gen_cards.py
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'lib', 'widgets', 'cards')

COMMON_FIELDS = '''
  /// The cards, back to front. Defaults to plain neutral cards.
  final List<Widget>? children;

  /// Drives the layout from outside. When null, hover (or tap on touch screens) drives it.
  final bool? hovered;

  /// Size of every card.
  final Size cardSize;

  /// Multiplies how far the cards travel and turn. 0 keeps them stacked.
  final double intensity;
'''

COMMON_PARAMS = 'this.children, this.hovered, this.cardSize = const Size(128, 176), this.intensity = 1'

NEUTRAL_SHELL = '''
Widget _shell(bool dark, Widget? child) => DecoratedBox(
      decoration: BoxDecoration(
        color: dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0x33E5E5E5)),
        boxShadow: const [
          BoxShadow(color: Color(0x26000000), blurRadius: 10, spreadRadius: -2, offset: Offset(0, 4)),
          BoxShadow(color: Color(0x1A000000), blurRadius: 6, spreadRadius: -2, offset: Offset(0, 2)),
        ],
      ),
      child: ClipRRect(borderRadius: BorderRadius.circular(15), child: child ?? const SizedBox.expand()),
    );
'''

LAYOUTS = [
    dict(
        cls='CardArc', file='card_arc', amicro='CardArc5 / CardArc7 / CardLongArc5',
        name='Arc', desc='cards that fan out along a gentle arc',
        usage='''//   CardArc()          // 5 cards
//   CardArc.seven()    // 7 cards, wider
//   CardArc.long()     // 5 cards, long and flat
//   CardArc(children: [for (final url in photos) Image.network(url, fit: BoxFit.cover)])''',
        ctor='''  const CardArc({
    super.key,
    COMMON,
    this.angle = 30,
    this.gap = 70,
    this.yOffset = 10,
    this.yProfile = const [-1, -0.2, 1],
  });

  /// Amicro's seven-card arc.
  const CardArc.seven({
    super.key,
    COMMON,
    this.angle = 45,
    this.gap = 110,
    this.yOffset = 30,
    this.yProfile = const [-0.5, -0.17, 0.33, 1],
  });

  /// Amicro's long arc: five cards spread wide with little tilt.
  const CardArc.long({
    super.key,
    COMMON,
    this.angle = 15,
    this.gap = 140,
    this.yOffset = 20,
    this.yProfile = const [-0.25, 0.25, 1],
  });''',
        fields='''
  /// Tilt of the outermost cards, in degrees.
  final double angle;

  /// Horizontal distance of the outermost cards from the centre.
  final double gap;

  /// Vertical scale of the arc.
  final double yOffset;

  /// Height of each card as a fraction of [yOffset], centre card first, outermost last.
  /// Its length sets the number of cards: n entries = 2n - 1 cards.
  final List<double> yProfile;
''',
        count='widget.yProfile.length * 2 - 1',
        pivot='Alignment.bottomCenter',
        z='-dist.abs()',
        spread='''final m = (_count - 1) / 2;
return _Pose(
  x: dist * (widget.gap / m) * k,
  y: widget.yProfile[dist.abs().round()] * widget.yOffset * k,
  rotate: dist * (widget.angle / m) * k,
  scale: dist == 0 ? 1.05 : 1,
);'''),
    dict(
        cls='CardLinearSpread', file='card_linear_spread', amicro='CardLinearSpread',
        name='Linear Spread', desc='a stack that slides apart into a straight row',
        usage='//   CardLinearSpread()',
        ctor='  const CardLinearSpread({super.key, COMMON, this.gap = 90});',
        fields='''
  /// Horizontal distance of the outermost cards from the centre.
  final double gap;
''',
        count='5', pivot='Alignment.center', z='-dist.abs()',
        spread='return _Pose(x: dist * (widget.gap / 2) * k, scale: dist == 0 ? 1.05 : 1);'),
    dict(
        cls='CardCornerFan', file='card_corner_fan', amicro='CardCornerFan',
        name='Corner Fan', desc='cards fanning out from their bottom-left corner, like a hand of cards',
        usage='//   CardCornerFan()',
        ctor='  const CardCornerFan({super.key, COMMON, this.angle = 40});',
        fields='''
  /// Total spread of the fan in degrees (it starts at -10).
  final double angle;
''',
        count='5', pivot='Alignment.bottomLeft', z='-(dist + centre)',  # the first card is on top
        spread='return _Pose(rotate: (-10 + i / (_count - 1) * widget.angle) * k, scale: i == 2 ? 1.03 : 1);'),
    dict(
        cls='CardStampArc', file='card_stamp_arc', amicro='CardStampArc',
        name='Stamp Arc', desc='perforated stamps dealt out along an arc',
        usage='''//   CardStampArc()
//   CardStampArc(colorful: true)''',
        ctor='''  const CardStampArc({
    super.key,
    COMMON,
    this.arc = 25,
    this.spread = 180,
    this.yOffset = 40,
    this.colorful = false,
  });''',
        fields='''
  /// Tilt of the outermost stamps, in degrees.
  final double arc;

  /// Horizontal distance of the outermost stamps from the centre.
  final double spread;

  /// How far the outer stamps drop below the centre one.
  final double yOffset;

  /// Red, blue, green, amber and purple stamps instead of neutral ones.
  final bool colorful;
''',
        count='5', pivot='Alignment.bottomCenter', z='-dist.abs()',
        spread='''const turn = [-1.0, -0.48, 0.0, 0.48, 1.0];
const across = [-1.0, -0.5, 0.0, 0.5, 1.0];
const drop = [1.0, 0.25, -0.25, 0.25, 1.0];
return _Pose(
  x: across[i] * widget.spread * k,
  y: drop[i] * widget.yOffset * k,
  rotate: turn[i] * widget.arc * k,
  scale: dist == 0 ? 1.05 : 1,
);''',
        shell_call='_stamp(dark, i, widget.colorful, child)',
        tail='''
const _stampColors = [
  (Color(0xFFF87171), Color(0xFFEF4444)), // red-400 / red-500
  (Color(0xFF60A5FA), Color(0xFF3B82F6)), // blue
  (Color(0xFF34D399), Color(0xFF10B981)), // emerald
  (Color(0xFFFBBF24), Color(0xFFF59E0B)), // amber
  (Color(0xFFC084FC), Color(0xFFA855F7)), // purple
];

Widget _stamp(bool dark, int i, bool colorful, Widget? child) {
  final (light, deep) = _stampColors[i % _stampColors.length];
  final fill = colorful ? (dark ? deep : light) : (dark ? const Color(0xFF262626) : const Color(0xFFA3A3A3));
  return DecoratedBox(
    decoration: BoxDecoration(
      color: fill,
      borderRadius: BorderRadius.circular(16),
      boxShadow: const [
        BoxShadow(color: Color(0x26000000), blurRadius: 10, spreadRadius: -2, offset: Offset(0, 4)),
        BoxShadow(color: Color(0x1A000000), blurRadius: 6, spreadRadius: -2, offset: Offset(0, 2)),
      ],
    ),
    child: CustomPaint(
      foregroundPainter: _DashedBorder(dark ? const Color(0x59000000) : const Color(0x99FFFFFF)),
      child: ClipRRect(borderRadius: BorderRadius.circular(16), child: child ?? const SizedBox.expand()),
    ),
  );
}

/// The perforated edge: a 2px dashed rounded border.
class _DashedBorder extends CustomPainter {
  _DashedBorder(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()..addRRect(RRect.fromRectAndRadius((Offset.zero & size).deflate(1), const Radius.circular(15)));
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = color;
    for (final metric in path.computeMetrics()) {
      for (double d = 0; d < metric.length; d += 10) {
        canvas.drawPath(metric.extractPath(d, math.min(d + 6, metric.length)), paint);
      }
    }
  }

  @override
  bool shouldRepaint(_DashedBorder old) => old.color != color;
}
'''),
    dict(
        cls='CardCascadeStagger', file='card_cascade_stagger', amicro='CardCascadeStagger',
        name='Cascade Stagger', desc='a pile that steps up diagonally, like a staircase of cards',
        usage='//   CardCascadeStagger()',
        ctor='  const CardCascadeStagger({super.key, COMMON});',
        fields='', count='5', pivot='Alignment.center', z='-dist.abs()',
        spring=(0.9, 200, 22),
        rest='return _Pose(y: dist * 2);',
        spread='''return _Pose(
  x: dist * 14 * k,
  y: (dist * -28 - 14) * k,
  rotate: dist * 6 * k,
  scale: dist == 0 ? 1.05 : 0.98,
);'''),
    dict(
        cls='CardScatterSpread', file='card_scatter_spread', amicro='CardScatterSpread',
        name='Scatter Spread', desc='cards dealt loosely onto a table, overlapping at odd angles',
        usage='//   CardScatterSpread()',
        ctor='  const CardScatterSpread({super.key, COMMON});',
        fields='', count='5', pivot='Alignment.center', z='-dist.abs()',
        spread='''const dealt = [(-75.0, 15.0, -14.0), (-35.0, -15.0, -6.0), (0.0, -30.0, 2.0), (35.0, -10.0, 8.0), (75.0, 20.0, 15.0)];
final (x, y, r) = dealt[i];
return _Pose(x: x * k, y: y * k, rotate: r * k, scale: i == 2 ? 1.05 : 0.98);'''),
    dict(
        cls='CardWheelFan', file='card_wheel_fan', amicro='CardWheelFan',
        name='Wheel Fan', desc='cards turning around a hub just below them, like a wheel',
        usage='//   CardWheelFan()',
        ctor='  const CardWheelFan({super.key, COMMON, this.step = 18});',
        fields='''
  /// Angle between neighbouring cards, in degrees.
  final double step;
''',
        count='5',
        # Pivot 10% below the cards' bottom edge (Motion's originY: 1.1).
        pivot='const Alignment(0, 1.2)', z='-dist.abs()',
        spread='''const lift = [-28.0, -22.0, -8.0]; // by distance from the centre
return _Pose(
  y: lift[dist.abs().round()] * k,
  rotate: dist * widget.step * k,
  scale: dist == 0 ? 1.05 : 0.98,
);'''),
]

TEMPLATE = '''// {cls} — {desc}.
//
// Copy this file into your project. It depends only on Flutter itself.
// Ported from Amicro's {amicro} (MIT, (c) 2026 Syed Subhan Uddin).
//
// Usage:
{usage}
//
// Hover (desktop/web) or tap (touch) to spread; pass `hovered` to drive it yourself.

import 'dart:math' as math;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

class {cls} extends StatefulWidget {{
{ctor}
{common_fields}{fields}
  @override
  State<{cls}> createState() => _{cls}State();
}}

class _{cls}State extends State<{cls}> with SingleTickerProviderStateMixin {{
  // 0 = resting pile, 1 = spread. A spring drives it, so reversing mid-flight keeps momentum.
  late final AnimationController _t = AnimationController.unbounded(
    vsync: this,
    value: (widget.hovered ?? false) ? 1 : 0,
  );
  bool _hover = false;

  static const _spring = SpringDescription(mass: {mass}, stiffness: {stiffness}, damping: {damping});

  bool get _active => widget.hovered ?? _hover;
  int get _count => {count};

  @override
  void didUpdateWidget({cls} oldWidget) {{
    super.didUpdateWidget(oldWidget);
    if (oldWidget.hovered != widget.hovered) _animate();
  }}

  @override
  void dispose() {{
    _t.dispose();
    super.dispose();
  }}

  void _setHover(bool value) {{
    if (widget.hovered != null || value == _hover) return;
    setState(() => _hover = value);
    _animate();
  }}

  void _animate() => _t.animateWith(SpringSimulation(_spring, _t.value, _active ? 1 : 0, _t.velocity));

  _Pose _rest(int i, double dist) {{
{rest}
  }}

  _Pose _spread(int i, double dist) {{
    final k = widget.intensity;
{spread}
  }}

  @override
  Widget build(BuildContext context) {{
    final dark = Theme.of(context).brightness == Brightness.dark;
    final children = widget.children;
    assert(children == null || children.length == _count, '{cls} needs exactly $_count children.');
    final centre = (_count - 1) / 2;
    // Paint the cards furthest back first, so the front card ends up on top.
    final order = [for (var i = 0; i < _count; i++) i]
      ..sort((a, b) {{
        double z(int i) {{
          final dist = i - centre;
          return {z};
        }}

        return z(a).compareTo(z(b));
      }});

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => _setHover(true),
      onExit: (_) => _setHover(false),
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        // Touch has no hover, so a tap toggles instead. (A mouse click would fight the hover.)
        onTapUp: (d) {{
          if (d.kind == PointerDeviceKind.touch) _setHover(!_hover);
        }},
        child: SizedBox.fromSize(
          size: widget.cardSize,
          child: AnimatedBuilder(
            animation: _t,
            builder: (context, _) => Stack(
              clipBehavior: Clip.none,
              children: [
                for (final i in order)
                  Positioned.fill(
                    key: ValueKey(i),
                    child: _card(i, i - centre, dark, children?[i]),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }}

  Widget _card(int i, double dist, bool dark, Widget? child) {{
    final p = _Pose.lerp(_rest(i, dist), _spread(i, dist), _t.value);
    return Transform(
      alignment: {pivot},
      transform: Matrix4.identity()
        ..translateByDouble(p.x, p.y, 0, 1)
        ..rotateZ(p.rotate * math.pi / 180)
        ..scaleByDouble(p.scale, p.scale, 1, 1),
      child: {shell_call},
    );
  }}
}}

/// Where a card sits: offset in pixels, rotation in degrees, and scale.
class _Pose {{
  const _Pose({{this.x = 0, this.y = 0, this.rotate = 0, this.scale = 1}});

  final double x, y, rotate, scale;

  static _Pose lerp(_Pose a, _Pose b, double t) => _Pose(
        x: a.x + (b.x - a.x) * t,
        y: a.y + (b.y - a.y) * t,
        rotate: a.rotate + (b.rotate - a.rotate) * t,
        scale: a.scale + (b.scale - a.scale) * t,
      );
}}
{shell}{tail}'''


def indent(s, n):
    return '\n'.join((' ' * n + line) if line.strip() else '' for line in s.strip('\n').split('\n'))


def main():
    for L in LAYOUTS:
        mass, stiffness, damping = L.get('spring', (0.8, 180, 20))
        src = TEMPLATE.format(
            cls=L['cls'], desc=L['desc'], amicro=L['amicro'], usage=L['usage'],
            ctor=L['ctor'].replace('COMMON', COMMON_PARAMS),
            common_fields=COMMON_FIELDS, fields=L['fields'],
            mass=mass, stiffness=stiffness, damping=damping, count=L['count'],
            rest=indent(L.get('rest', 'return const _Pose();'), 4),
            spread=indent(L['spread'], 4), z=L['z'], pivot=L['pivot'],
            shell_call=L.get('shell_call', '_shell(dark, child)'),
            shell=NEUTRAL_SHELL if 'shell_call' not in L else '',
            tail=L.get('tail', ''))
        with open(os.path.join(OUT, L['file'] + '.dart'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(src)

    # Library exports for the generated cards (kept together, after the hand-written cards).
    lib = os.path.join(ROOT, 'lib', 'flutter_motion_kit.dart')
    s = open(lib, encoding='utf-8').read()
    generated = [f"export 'widgets/cards/{L['file']}.dart';\n" for L in LAYOUTS]
    for line in generated:
        s = s.replace(line, '')
    anchor = "export 'widgets/cards/linear_spread.dart';\n"
    s = s.replace(anchor, anchor + ''.join(generated))
    with open(lib, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)

    # Gallery catalogue.
    cat = os.path.join(ROOT, 'example', 'lib', 'card_catalog.g.dart')
    entries = [
        ('Arc 5', 'CardArc', 'const CardArc()', 'card_arc'),
        ('Arc 7', 'CardArc', 'const CardArc.seven()', 'card_arc'),
        ('Long Arc 5', 'CardArc', 'const CardArc.long()', 'card_arc'),
    ] + [(L['name'], L['cls'], f"const {L['cls']}()", L['file']) for L in LAYOUTS[1:]]
    entries.insert(6, ('Stamp Arc · Colorful', 'CardStampArc', 'const CardStampArc(colorful: true)', 'card_stamp_arc'))
    with open(cat, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// GENERATED by tool/gen_cards.py. Do not edit.\n')
        fh.write("import 'package:flutter/widgets.dart';\n")
        fh.write("import 'package:flutter_motion_kit/flutter_motion_kit.dart';\n\n")
        fh.write('typedef CardEntry = ({String name, String source, Widget Function(bool hovered) builder});\n\n')
        fh.write('final List<CardEntry> hoverCardCatalog = [\n')
        for name, cls, ctor, file in entries:
            call = ctor.replace('const ', '').replace('()', '(hovered: hovered)').replace('(colorful: true)', '(colorful: true, hovered: hovered)')
            fh.write(f"  (name: {name!r}, source: 'cards/{file}.dart', builder: (hovered) => {call}),\n")
        fh.write('];\n')
    print(f'Generated {len(LAYOUTS)} card layouts ({len(entries)} gallery entries)')


if __name__ == '__main__':
    main()
