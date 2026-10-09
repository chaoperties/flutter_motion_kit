"""Generate 28 standalone Mono Charts and the gallery's 30 previews.

Run python tool/gen_mono_charts.py, format Dart, then sync example sources.
The rounded geometry and demo datasets follow Amicro's MIT Mono Charts.
Shared mechanics are emitted into every file to preserve the copy-paste rule.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = (ROOT / 'tool/mono_chart.dart.tmpl').read_text(encoding='utf-8')


def series(labels, values, **extras):
    return [dict(label=label, value=value, **{key: items[i] for key, items in extras.items()})
            for i, (label, value) in enumerate(zip(labels, values))]


WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
LINE = {
    '24H': series(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                  [124, 132, 158, 168, 152, 146, 142], secondary=[155, 158, 172, 180, 170, 164, 160]),
    '1H': series(['00m', '10m', '20m', '30m', '40m', '50m', '60m'],
                 [138, 142, 135, 148, 140, 144, 142], secondary=[160, 158, 162, 165, 159, 161, 160]),
    '7D': series(WEEK, [134, 145, 138, 165, 152, 128, 142], secondary=[150, 162, 159, 178, 168, 148, 160]),
}
BAR = {
    '7D': series(WEEK, [4120, 4780, 4420, 5190, 4980, 4240, 4892], secondary=[1250, 1420, 1310, 1580, 1500, 1210, 1440]),
    '30D': series(['W1', 'W2', 'W3', 'W4'], [3950, 4320, 4680, 5120], secondary=[1100, 1280, 1390, 1540]),
}
CHARTS = []


def add(suffix, title, kind, data, unit='', fields=None, metric=None, detail=None):
    cls = 'Mono' + suffix
    file = re.sub(r'(?<!^)(?=[A-Z])', '_', cls).lower()
    CHARTS.append(dict(cls=cls, point=cls.replace('Chart', '') + 'Point', file=file,
                       title=title, kind=kind, datasets=data if isinstance(data, dict) else {'Default': data},
                       unit=unit, fields=fields or {}, metric=metric, detail=detail))


activity = series([f'Week {i // 7 + 1}, day {i % 7 + 1}' for i in range(140)],
                  [0 if (i * 17 + 3) % 11 < 4 else ((i * 13 + 5) % 16 + 1) for i in range(140)])
add('ActivityHeatmap', 'Activity Heatmap', 'activity', activity, 'commits',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value))')
add('RoundedLineChart', 'Rounded Spline Line', 'line', LINE, 'ms', {'secondary': ('double', '0')})
add('RoundedBarChart', 'Rounded Pill Pillars', 'bar', BAR, 'tx/s', {'secondary': ('double', '0')})
area_data = series(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'], [8.4, 11.2, 16.5, 19.8, 18.4, 14.6, 12.1])
add('RoundedAreaChart', 'Curved Wave Area', 'area', {'Smooth': area_data, 'Linear': area_data}, 'Gbps')
add('RoundedDonutChart', 'Rounded Donut Ring', 'donut',
    series(['Core Stake', 'Liquidity Pool', 'Insurance Fund', 'Ecosystem'], [45, 30, 15, 10]), '% allocation',
    metric='_number(data.fold<double>(0, (sum, d) => sum + math.max(0, d.value)))')
composed = series([f'Ep. {i}' for i in range(420, 426)], [184, 210, 242, 206, 275, 298], secondary=[7.2, 7.5, 7.8, 7.6, 8.1, 8.4])
add('RoundedComposedChart', 'Hybrid Spline + Bar', 'composed', {'All': composed, 'Rewards': composed, 'APY': composed}, 'rewards', {'secondary': ('double', '0')},
    detail="'${d.label}: ${_number(d.value)} rewards · ${_number(d.secondary)}% APY'")
nodes = series(['Validator Alpha', 'Staking Prime', 'SolNode 04', 'Nexus Stake', 'Helios Node', 'Apex Validator', 'Atlas Core'],
               [1450, 890, 640, 1120, 420, 310, 980], x=[18, 26, 34, 42, 55, 68, 22], size=[280, 220, 180, 260, 140, 120, 240])
add('RoundedScatterChart', 'Scatter Matrix', 'scatter', {'All': nodes, 'Leaders': [nodes[i] for i in [0, 1, 3, 6]]}, 'stake',
    {'x': ('double', '0'), 'size': ('double', '100')}, detail="'${d.label}: ${_number(d.x)} ms · ${_number(d.value)} stake'")
candles = {
    '15M': series(['14:00', '14:15', '14:30', '14:45', '15:00'], [174.2, 175.8, 174.6, 177.2, 178.4],
                  open=[172.5, 174.2, 175.8, 174.6, 177.2], low=[171.8, 173.9, 174.1, 174.4, 176.5], high=[174.8, 176.5, 176.2, 177.8, 179.5]),
    '1H': series(['11:00', '12:00', '13:00', '14:00', '15:00'], [170.8, 172.5, 174.2, 177.2, 178.4],
                 open=[168, 170.8, 172.5, 174.2, 177.2], low=[167.5, 169.8, 171.9, 173.8, 176], high=[171.2, 173.5, 175, 177.8, 180.2]),
    '4H': series(['00:00', '04:00', '08:00', '12:00'], [165.8, 169.4, 173.6, 178.4],
                 open=[162, 165.8, 169.4, 173.6], low=[161.2, 164.5, 168.2, 172.5], high=[166.5, 170.2, 174.8, 180.2]),
}
add('RoundedCandlestickChart', 'Financial Candlesticks', 'candle', candles, 'USD',
    {'open': ('double', '0'), 'low': ('double', '0'), 'high': ('double', '0')},
    detail="'${d.label}: O ${_number(d.open)} · H ${_number(d.high)} · L ${_number(d.low)} · C ${_number(d.value)}'")
add('RoundedKpiCardChart', 'Stat KPI Card', 'kpi', {
    'YoY': series(['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov'], [240, 285, 320, 390, 430, 482.9]),
    'MoM': series(['W1', 'W2', 'W3', 'W4'], [462, 468, 474, 482.9]),
}, 'k USD')
add('RoundedPyramidChart', 'Tier Pyramid Stack', 'pyramid',
    series(['Finalized Block', 'Banking Consensus', 'SigVerify Queue', 'Network Inbound'], [34, 54, 74, 94]), '%', metric='_number(data.first.value)')
add('RoundedRadialBarGroup', 'Radial Bar Group', 'radial_group',
    series(['Compute (CPU)', 'Memory Pool', 'NVMe Bandwidth', 'Network Buffer'], [88, 72, 56, 42]), '% utilization',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value) / data.length)')
add('RoundedGaugeArc', 'Speedometer Gauge Arc', 'gauge',
    {'Enterprise': series(['Uptime'], [99.98]), 'Standard': series(['Uptime'], [99.5])}, '% uptime')
add('RoundedBulletChart', 'Performance Bullet Target', 'bullet',
    series(['Block Time', 'Vote Success', 'Cluster Throughput'], [380, 98.6, 4850], target=[400, 95, 4500]), '',
    {'target': ('double', '100')}, detail="'${d.label}: ${_number(d.value)} / target ${_number(d.target)}'")
add('RoundedSankeyChart', 'Flow Sankey Channels', 'sankey', series(['Mempool', 'RPC Direct'], [48.5, 35.7]), 'k tx/s',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value))')
steps = series(['Min', 'Low', 'Median', 'Fast', 'Turbo', 'Max'], [5, 12.4, 24.8, 42, 68.5, 95])
add('RoundedStepChart', 'Step Progression', 'step', {'All': steps, 'Priority': steps[2:]}, 'fee')
add('RoundedStackedBarChart', 'Stacked Tones Bar', 'stacked',
    series(['04:00', '08:00', '12:00', '16:00', '20:00', '24:00'], [3.2, 4.8, 6.4, 7.2, 5.6, 4.2],
           secondary=[2.1, 2.9, 3.8, 4.1, 3.4, 2.6], tertiary=[1.4, 1.8, 2.2, 2.6, 2.0, 1.6]), 'M volume',
    {'secondary': ('double', '0'), 'tertiary': ('double', '0')})
add('RoundedRadarChart', 'Polygon Web Radar', 'radar',
    series(['Finality', 'Uptime', 'Peer Quality', 'SigVerify', 'Stake Weight'], [95, 99, 88, 92, 86]), '/ 100',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value) / data.length)')
add('RoundedRadialGaugeChart', 'Concentric Radial Rings', 'radial_gauge',
    series(['Compute Units', 'Request Quota', 'Burst Bandwidth'], [84, 68, 45]), '% consumed', metric='_number(data.first.value)')
add('RoundedFunnelChart', 'Stage Funnel', 'funnel',
    series(['Site Visitor', 'Wallet Connect', 'First Tx', 'Recurring'], [100, 68, 44, 26]), '% conversion')
hours = [[14, 38, 72, 54, 88, 32, 58], [28, 56, 84, 68, 42, 76, 24], [48, 68, 34, 78, 62, 92, 44],
         [22, 76, 58, 44, 94, 52, 68], [58, 88, 66, 84, 48, 36, 74]]
add('RoundedHeatmapChart', 'Dot Matrix Heatmap', 'heatmap',
    [dict(label=f'{WEEK[r]} {c * 4:02d}h', value=val) for r, row in enumerate(hours) for c, val in enumerate(row)], '% load',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value) / data.length)')
add('RoundedSparklineChart', 'Sparkline Telemetry', 'sparkline',
    series(['CPU Core Temp', 'NVMe IOPS', 'Memory Pool'], [42.4, 48.2, 18.4],
           history=[[38, 41, 39, 44, 42.4], [28, 34, 42, 49, 48.2], [14, 16, 17.5, 18.8, 18.4]]), '',
    {'history': ('List<double>', 'const []')})
add('RoundedBubbleChart', 'Bubble Clusters', 'bubble',
    series(['SOL / USDC', 'SOL / USDT', 'JUP / SOL', 'BONK / SOL'], [18.5, 14.2, 24.8, 32.4], x=[180, 95, 64, 38], size=[750, 480, 360, 280]), '% APY',
    {'x': ('double', '0'), 'size': ('double', '100')}, detail="'${d.label}: ${_number(d.x)}M volume · ${_number(d.value)}% APY'")
add('RoundedTreemapChart', 'Tile Treemap', 'treemap',
    series(['Accounts DB', 'Snapshots', 'Index Cache', 'Mempool'], [48, 28, 14, 10]), '% share',
    metric='_number(data.fold<double>(0, (sum, d) => sum + d.value))')
add('RoundedStreamChart', 'Fluid Stream Wave', 'stream',
    series(['00h', '04h', '08h', '12h', '16h', '20h'], [28, 42, 58, 84, 76, 64], secondary=[18, 24, 36, 48, 52, 38]), 'M volume',
    {'secondary': ('double', '0')})
add('RoundedMeterChart', 'Arc Meter Gauge', 'meter', series(['Efficiency'], [88]), '% efficiency')
add('RoundedWaterfallChart', 'Waterfall Steps', 'waterfall',
    series(['Opening', 'Yield', 'Infra', 'Grants', 'Closing'], [120, 45, -18, -12, 135], base=[0, 120, 165, 147, 0]), 'k USD',
    {'base': ('double', '0')})
add('RoundedPolarChart', 'Polar Radial Pillars', 'polar',
    series(['US-East', 'EU-Central', 'AP-South', 'SA-East'], [95, 72, 54, 32]), '% requests')
add('RoundedRangeChart', 'Range Band Area', 'range',
    series(WEEK, [0.28, 0.35, 0.30, 0.42, 0.38, 0.25, 0.29], low=[0.12, 0.15, 0.14, 0.18, 0.16, 0.11, 0.13]), 'variance',
    {'low': ('double', '0')}, detail="'${d.label}: ${_number(d.low)}–${_number(d.value)} ${widget.unit}'")

CARTESIAN = r'''
  Rect plot(Size size) => Rect.fromLTRB(38, 14, math.max(39, size.width - 16), math.max(15, size.height - 26));
  (double, double) get domain {
    final values = <double>[for (final d in data) ...[__DOMAIN_VALUES__]];
    final low = __DOMAIN_LOW__;
    final high = values.reduce(math.max);
    final span = high - low;
    final pad = span.abs() < 0.000001 ? math.max(high.abs() * 0.1, 1.0) : span * 0.12;
    return (low == 0 ? 0.0 : low - pad, high + pad);
  }
  double y(double value, Rect r) {
    final (low, high) = domain;
    return r.bottom - (value - low) / (high - low) * r.height;
  }
  double x(int i, Rect r) => r.left + (i + 0.5) * r.width / data.length;
  void axes(Canvas canvas, Rect r) {
    final (low, high) = domain;
    for (var i = 0; i <= 3; i++) {
      final yy = r.top + r.height * i / 3;
      canvas.drawLine(Offset(r.left, yy), Offset(r.right, yy), stroke(text.withValues(alpha: 0.06), 1));
      label(canvas, _number(high - (high - low) * i / 3), Offset(3, yy - 5), fontSize: 9);
    }
    final step = math.max(1, (data.length / 5).ceil());
    for (var i = 0; i < data.length; i += step) {
      label(canvas, data[i].label, Offset(x(i, r), r.bottom + 7), centered: true, fontSize: 9);
    }
  }
'''
CURVE = r'''
  Path curve(List<Offset> points) {
    final path = Path();
    if (points.isEmpty) return path;
    path.moveTo(points.first.dx, points.first.dy);
    if (mode == 'Linear') {
      for (final p in points.skip(1)) { path.lineTo(p.dx, p.dy); }
      return path;
    }
    for (var i = 1; i < points.length; i++) {
      final a = points[i - 1], b = points[i];
      final mid = (a.dx + b.dx) / 2;
      path.cubicTo(mid, a.dy, mid, b.dy, b.dx, b.dy);
    }
    return path;
  }
'''
HIT_X = r'''
    final r = plot(size);
    if (!r.contains(position)) return null;
    return ((position.dx - r.left) / r.width * data.length).floor().clamp(0, data.length - 1);
'''
NEAREST = r'''
    final positions = anchors(size);
    var best = 0;
    var distance = double.infinity;
    for (var i = 0; i < positions.length; i++) {
      final candidate = (positions[i] - position).distance;
      if (candidate < distance) { best = i; distance = candidate; }
    }
    return distance <= 28 ? best : null;
'''
PAINTERS = {}


def cart(kind, body, values='d.value', low='math.min(0.0, values.reduce(math.min))', curve=False, hit=HIT_X, extra=''):
    helpers = CARTESIAN.replace('__DOMAIN_VALUES__', values).replace('__DOMAIN_LOW__', low)
    PAINTERS[kind] = (helpers + (CURVE if curve else '') + extra, hit, body)


def generation():
    out = ROOT / 'lib/widgets/charts'
    out.mkdir(parents=True, exist_ok=True)
    exports = []
    catalog = ["// GENERATED by tool/gen_mono_charts.py. Do not edit.",
               "import 'package:flutter/material.dart';", "import 'package:flutter_motion_kit/flutter_motion_kit.dart';",
               "typedef MonoChartEntry = ({String name, String source, WidgetBuilder builder});",
               'final List<MonoChartEntry> monoChartCatalog = [']
    for spec in CHARTS:
        cls, point, fields = spec['cls'], spec['point'], spec['fields']
        defaults = []
        for key, rows in spec['datasets'].items():
            defaults.append(f"  '{key}': [")
            for row in rows:
                params = ', '.join(f'{key}: {dart(value)}' for key, value in row.items())
                defaults.append(f'    {point}({params}),')
            defaults.append('  ],')
        helpers, hit, body = PAINTERS[spec['kind']]
        valid = ''.join(f' && d.{key}.isFinite' if typ == 'double' else f' && d.{key}.every((v) => v.isFinite)'
                        for key, (typ, _) in fields.items())
        default_detail = "'${d.label}: ${_number(d.value)} ${widget.unit}'"
        if 'secondary' in fields:
            default_detail = "'${d.label}: ${_number(d.value)} / ${_number(d.secondary)} ${widget.unit}'"
        if 'tertiary' in fields:
            default_detail = "'${d.label}: ${_number(d.value)} / ${_number(d.secondary)} / ${_number(d.tertiary)} ${widget.unit}'"
        spec_values = dict(CLASS=cls, POINT=point, TITLE=spec['title'], UNIT=spec['unit'],
                           PARAMS=', '.join(f'this.{key} = {default}' for key, (_, default) in fields.items()),
                           FIELDS='\n'.join(f'  final {typ} {key};' for key, (typ, _) in fields.items()),
                           DEFAULTS='\n'.join(defaults), VALID=valid,
                           INK='const Color(0xFF39D353)' if spec['kind'] == 'activity' else '(dark ? Colors.white : const Color(0xFF09090B))',
                           METRIC=spec['metric'] or '_number(data.last.value)',
                           DETAIL=spec['detail'] or default_detail,
                           HELPERS=helpers, HIT=hit, BODY=body)
        text = TEMPLATE
        for key, value in spec_values.items():
            text = text.replace(f'__{key}__', value)
        (out / f"{spec['file']}.dart").write_text(text, encoding='utf-8')
        exports.append(f"export 'widgets/charts/{spec['file']}.dart';")
        variants = [('Emerald Activity Heatmap', ''), ('Sky Blue Activity Heatmap', ', color: Color(0xFF38BDF8)'),
                    ('Violet Activity Heatmap', ', color: Color(0xFFC084FC)')] if spec['kind'] == 'activity' else [(spec['title'], '')]
        for title, params in variants:
            catalog.append(f"  (name: '{title}', source: 'charts/{spec['file']}.dart', builder: (_) => const {cls}(width: 420, height: 260{params})),")
    catalog.append('];')
    (ROOT / 'example/lib/mono_chart_catalog.g.dart').write_text('\n'.join(catalog) + '\n', encoding='utf-8')
    library = ROOT / 'lib/flutter_motion_kit.dart'
    original = library.read_text(encoding='utf-8')
    original = re.sub(r"^export 'widgets/charts/.*';\n?", '', original, flags=re.M)
    library.write_text(original.rstrip() + '\n' + '\n'.join(exports) + '\n', encoding='utf-8')
    print(f'Generated {len(CHARTS)} chart widgets and 30 gallery previews.')


def dart(value):
    if isinstance(value, str):
        return "'" + value.replace("'", "\\'") + "'"
    if isinstance(value, list):
        return '[' + ', '.join(dart(item) for item in value) + ']'
    return str(value)


# Painter definitions follow below. Each widget receives only its own geometry.
for kind in ['line', 'area', 'kpi', 'step', 'range', 'stream']:
    body = r'''
    final r = plot(size);
    axes(canvas, r);
    final points = [for (var i = 0; i < data.length; i++) Offset(x(i, r), y(data[i].value, r))];
    canvas.save();
    canvas.clipRect(Rect.fromLTRB(r.left, r.top, r.left + r.width * progress, r.bottom + 2));
'''
    if kind == 'line':
        body += r'''
    final secondary = [for (var i = 0; i < data.length; i++) Offset(x(i, r), y(data[i].secondary, r))];
    canvas.drawPath(curve(secondary), stroke(ink.withValues(alpha: 0.3), 1.5));
'''
    if kind in ['area', 'kpi']:
        body += r'''
    final area = curve(points)..lineTo(points.last.dx, y(0, r))..lineTo(points.first.dx, y(0, r))..close();
    canvas.drawPath(area, Paint()..shader = LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter,
      colors: [ink.withValues(alpha: 0.32), ink.withValues(alpha: 0.01)]).createShader(r));
'''
    if kind == 'range':
        body += r'''
    final lower = [for (var i = 0; i < data.length; i++) Offset(x(i, r), y(data[i].low, r))];
    final band = curve(points);
    final reversed = lower.reversed.toList();
    band.lineTo(reversed.first.dx, reversed.first.dy);
    for (var i = 1; i < reversed.length; i++) {
      final a = reversed[i - 1], b = reversed[i], mid = (a.dx + b.dx) / 2;
      band.cubicTo(mid, a.dy, mid, b.dy, b.dx, b.dy);
    }
    band.close();
    canvas.drawPath(band, fill(ink.withValues(alpha: 0.18)));
    canvas.drawPath(curve(lower), stroke(ink.withValues(alpha: 0.4), 2));
'''
    if kind == 'stream':
        body += r'''
    final upper = [for (var i = 0; i < data.length; i++) Offset(x(i, r), y(data[i].value + data[i].secondary, r))];
    final all = curve(upper)..lineTo(upper.last.dx, y(0, r))..lineTo(upper.first.dx, y(0, r))..close();
    final bottom = curve(points)..lineTo(points.last.dx, y(0, r))..lineTo(points.first.dx, y(0, r))..close();
    canvas.drawPath(all, fill(ink.withValues(alpha: 0.2)));
    canvas.drawPath(bottom, fill(ink.withValues(alpha: 0.4)));
    canvas.drawPath(curve(upper), stroke(ink.withValues(alpha: 0.6), 2));
'''
    if kind == 'step':
        body += r'''
    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) {
      path.lineTo(points[i].dx, points[i - 1].dy);
      path.lineTo(points[i].dx, points[i].dy);
    }
    canvas.drawPath(path, stroke(ink, 3));
'''
    else:
        body += '    canvas.drawPath(curve(points), stroke(ink, 3));\n'
    body += r'''
    for (var i = 0; i < points.length; i++) {
      canvas.drawCircle(points[i], selected == i ? 5.5 : 3, fill(tone(0)));
    }
    canvas.restore();
'''
    values = {'line': 'd.value, d.secondary', 'range': 'd.value, d.low',
              'stream': 'd.value, d.value + d.secondary'}.get(kind, 'd.value')
    cart(kind, body, values=values, curve=kind != 'step',
         low='values.reduce(math.min)' if kind == 'line' else 'math.min(0.0, values.reduce(math.min))')

for kind in ['bar', 'stacked', 'waterfall', 'composed', 'candle']:
    body = r'''
    final r = plot(size);
    axes(canvas, r);
    final slot = r.width / data.length;
    final width = math.min(24.0, slot * 0.55);
    for (var i = 0; i < data.length; i++) {
      final d = data[i];
      final xx = x(i, r);
'''
    if kind == 'bar':
        body += r'''
      for (var j = 0; j < 2; j++) {
        final value = (j == 0 ? d.value : d.secondary) * progress;
        final top = math.min(y(value, r), y(0, r)), bottom = math.max(y(value, r), y(0, r));
        final box = Rect.fromLTRB(xx + (j == 0 ? -width : 2), top, xx + (j == 0 ? -2 : width), bottom);
        canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(7)), fill(tone(j)));
      }
'''
    elif kind == 'stacked':
        body += r'''
      var base = 0.0;
      for (var j = 0; j < 3; j++) {
        final value = math.max(0, [d.value, d.secondary, d.tertiary][j]) * progress;
        final box = Rect.fromLTRB(xx - width / 2, y(base + value, r) + 1, xx + width / 2, y(base, r) - 1);
        if (box.height > 0) { canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(5)), fill(tone(j))); }
        base += value;
      }
'''
    elif kind == 'waterfall':
        body += r'''
      final end = d.base + d.value * progress;
      final box = Rect.fromLTRB(xx - width / 2, y(math.max(d.base, end), r), xx + width / 2, y(math.min(d.base, end), r));
      canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(6)), fill(tone(d.value < 0 ? 3 : 0)));
      if (i + 1 < data.length && i > 0) { canvas.drawLine(Offset(xx + width / 2, y(end, r)),
        Offset(x(i + 1, r) - width / 2, y(end, r)), stroke(ink.withValues(alpha: 0.25), 1)); }
'''
    elif kind == 'candle':
        body += r'''
      final high = math.max(d.high, math.max(d.open, d.value));
      final low = math.min(d.low, math.min(d.open, d.value));
      canvas.drawLine(Offset(xx, y(high, r)), Offset(xx, y(low, r)), stroke(tone(0), 1.5));
      final top = y(math.max(d.open, d.value), r);
      final bottom = math.max(top + 2, y(math.min(d.open, d.value), r));
      final box = RRect.fromRectAndRadius(Rect.fromLTRB(xx - width / 2, top, xx + width / 2, bottom), const Radius.circular(4));
      canvas.drawRRect(box, d.value >= d.open ? fill(tone(0).withValues(alpha: progress)) : stroke(tone(0).withValues(alpha: progress), 2));
'''
    else:
        body += r'''
      final top = y(d.value * progress, r), bottom = y(0, r);
      final box = Rect.fromLTRB(xx - width / 2, math.min(top, bottom), xx + width / 2, math.max(top, bottom));
      if (mode != 'APY') { canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(7)), fill(tone(2))); }
'''
    body += r'''
      if (selected == i) { canvas.drawLine(Offset(xx, r.top), Offset(xx, r.bottom), stroke(ink.withValues(alpha: 0.25), 1)); }
    }
'''
    if kind == 'composed':
        body += r'''
    final maxSecondary = math.max(1.0, data.map((d) => d.secondary.abs()).reduce(math.max));
    final points = [for (var i = 0; i < data.length; i++) Offset(x(i, r), r.bottom - data[i].secondary / maxSecondary * r.height * 0.85 * progress)];
    if (mode != 'Rewards') {
      canvas.drawPath(curve(points), stroke(ink, 3));
      for (final p in points) { canvas.drawCircle(p, 3, fill(tone(0))); }
      label(canvas, 'APY (right)', Offset(r.right - 70, r.top), fontSize: 9);
      label(canvas, _number(maxSecondary), Offset(r.right - 20, r.top + 15), fontSize: 9);
    }
'''
    values = {'bar': 'd.value, d.secondary', 'stacked': 'd.value + math.max(0, d.secondary) + math.max(0, d.tertiary)',
              'waterfall': 'd.base, d.base + d.value', 'candle': 'd.value, d.open, d.low, d.high'}.get(kind, 'd.value')
    cart(kind, body, values=values, curve=kind == 'composed',
         low='values.reduce(math.min)' if kind == 'candle' else 'math.min(0.0, values.reduce(math.min))')

SCATTER_HELPERS = r'''
  double get minX => math.min(0.0, data.map((d) => d.x).reduce(math.min));
  double get maxX => math.max(minX + 1, data.map((d) => d.x).reduce(math.max) * 1.12);
  List<Offset> anchors(Size size) {
    final r = plot(size);
    return [for (final d in data) Offset(r.left + (d.x - minX) / (maxX - minX) * r.width, y(d.value, r))];
  }
'''
for kind in ['scatter', 'bubble']:
    body = r'''
    final r = plot(size);
    axes(canvas, r);
    final points = anchors(size);
    final maxSize = math.max(1.0, data.map((d) => d.size.abs()).reduce(math.max));
    for (var i = 0; i < data.length; i++) {
      final radius = __RADIUS__ * progress;
      canvas.drawCircle(points[i], radius, fill(tone(i).withValues(alpha: selected == i ? 0.8 : 0.28)));
      canvas.drawCircle(points[i], radius, stroke(tone(i), selected == i ? 2.5 : 1.5));
    }
    label(canvas, _number(minX), Offset(r.left, r.bottom + 7), fontSize: 9);
    label(canvas, _number(maxX), Offset(r.right - 22, r.bottom + 7), fontSize: 9);
'''
    radius = '(5 + math.sqrt(math.max(0, data[i].size) / maxSize) * 5)' if kind == 'scatter' else '(8 + math.sqrt(math.max(0, data[i].size) / maxSize) * math.min(27, r.height * 0.18))'
    # Scatter axes use numeric x ticks, not observation names.
    scatter_cart = CARTESIAN.replace('__DOMAIN_VALUES__', 'd.value').replace('__DOMAIN_LOW__', 'math.min(0.0, values.reduce(math.min))')
    start = scatter_cart.index('    final step =')
    scatter_cart = scatter_cart[:start] + '  }\n'
    PAINTERS[kind] = (scatter_cart + SCATTER_HELPERS, NEAREST, body.replace('__RADIUS__', radius))

HEAT_HELPERS = r'''
  List<Rect> cells(Size size) {
    const rows = __ROWS__;
    final cols = (data.length / rows).ceil();
    final r = Rect.fromLTRB(30, 24, size.width - 12, size.height - 24);
    final width = r.width / cols, height = r.height / rows;
    return [for (var i = 0; i < data.length; i++) Rect.fromLTWH(
      r.left + __COL__ * width + 2, r.top + __ROW__ * height + 2,
      math.max(0, width - 4), math.max(0, height - 4))];
  }
'''
HIT_CELLS = r'''
    final boxes = cells(size);
    for (var i = 0; i < boxes.length; i++) { if (boxes[i].contains(position)) return i; }
    return null;
'''
for kind in ['activity', 'heatmap']:
    helpers = HEAT_HELPERS.replace('__ROWS__', '7' if kind == 'activity' else '5')
    helpers = helpers.replace('__COL__', '(i ~/ rows)' if kind == 'activity' else '(i % cols)')
    helpers = helpers.replace('__ROW__', '(i % rows)' if kind == 'activity' else '(i ~/ cols)')
    body = r'''
    final boxes = cells(size);
    final maxValue = math.max(1.0, data.map((d) => d.value).reduce(math.max));
    for (var i = 0; i < boxes.length; i++) {
      final opacity = (0.06 + math.max(0, data[i].value) / maxValue * 0.94) * progress;
      final rr = RRect.fromRectAndRadius(boxes[i], const Radius.circular(3));
      canvas.drawRRect(rr, fill(tone(0).withValues(alpha: opacity.clamp(0, 1))));
      if (selected == i) canvas.drawRRect(rr, stroke(text, 1.5));
    }
'''
    if kind == 'activity':
        body += r'''
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    for (var i = 0; i < math.min(7, boxes.length); i++) {
      label(canvas, days[i], Offset(9, boxes[i].center.dy - 5), fontSize: 9);
    }
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May'];
    for (var i = 0; i < 5; i++) {
      label(canvas, months[i], Offset(30 + i * (size.width - 42) / 5, 6), fontSize: 9);
    }
    label(canvas, 'Less', Offset(30, size.height - 16), fontSize: 9);
    for (var i = 0; i < 5; i++) {
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(size.width - 100 + i * 12, size.height - 16, 9, 9),
        const Radius.circular(2)), fill(ink.withValues(alpha: 0.08 + i * 0.23)));
    }
    label(canvas, 'More', Offset(size.width - 36, size.height - 17), fontSize: 9);
'''
    else:
        body += r'''
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    final cols = (data.length / 5).ceil();
    for (var i = 0; i < 5 && i * cols < boxes.length; i++) {
      label(canvas, days[i], Offset(1, boxes[i * cols].center.dy - 4), fontSize: 8);
    }
    for (var i = 0; i < cols; i++) {
      label(canvas, '${i * 4}h', Offset(boxes[i].center.dx, 6), centered: true, fontSize: 9);
    }
'''
    PAINTERS[kind] = (helpers, HIT_CELLS, body)

PAINTERS['donut'] = (r'''
  double get total => data.fold<double>(0, (sum, d) => sum + math.max(0, d.value));
  Offset center(Size size) => Offset(size.width / 2, size.height / 2);
  double radius(Size size) => math.min(size.width, size.height) * 0.34;
''', r'''
    if (total <= 0) return null;
    final v = position - center(size), rr = radius(size);
    if ((v.distance - rr).abs() > rr * 0.24) return null;
    final angle = (math.atan2(v.dy, v.dx) + math.pi / 2 + math.pi * 2) % (math.pi * 2);
    var start = 0.0;
    for (var i = 0; i < data.length; i++) {
      final sweep = math.max(0, data[i].value) / total * math.pi * 2;
      if (angle >= start + 0.03 && angle <= start + sweep - 0.03) return i;
      start += sweep;
    }
    return null;
''', r'''
    final c = center(size), rr = radius(size), box = Rect.fromCircle(center: c, radius: rr);
    canvas.drawCircle(c, rr, stroke(ink.withValues(alpha: 0.06), rr * 0.35));
    var start = -math.pi / 2;
    for (var i = 0; i < data.length; i++) {
      final sweep = total <= 0 ? 0.0 : math.max(0, data[i].value) / total * math.pi * 2;
      if (sweep > 0.08) { canvas.drawArc(box, start + 0.04, (sweep - 0.08) * progress, false, stroke(tone(i), rr * 0.35)); }
      start += sweep;
    }
    label(canvas, selected == null ? _number(total) : '${_number(data[selected!].value)}%', c - const Offset(0, 12),
      color: text, fontSize: 22, centered: true);
    label(canvas, 'Allocation', c + const Offset(0, 14), centered: true);
''')

RADIAL_HELPERS = r'''
  Offset center(Size size) => Offset(size.width / 2, size.height / 2);
  double outer(Size size) => math.min(size.width, size.height) * 0.42;
  double spacing(Size size) => outer(size) / (data.length + 1);
'''
for kind in ['radial_group', 'radial_gauge', 'polar']:
    sweep = 'math.pi * 1.5' if kind == 'radial_group' else 'math.pi * 2 - 0.08'
    body = r'''
    final c = center(size), gap = spacing(size);
    for (var i = 0; i < data.length; i++) {
      final radius = outer(size) - i * gap;
      final rect = Rect.fromCircle(center: c, radius: radius);
      final width = math.max(2.0, gap * 0.55);
      canvas.drawArc(rect, -math.pi / 2, __SWEEP__, false, stroke(ink.withValues(alpha: 0.07), width));
      canvas.drawArc(rect, -math.pi / 2, __SWEEP__ * (data[i].value / 100).clamp(0, 1) * progress,
        false, stroke(tone(i), width));
    }
    label(canvas, selected == null ? '${_number(data.first.value)}%' : '${_number(data[selected!].value)}%',
      c - const Offset(0, 8), centered: true, color: text, fontSize: 15);
'''
    PAINTERS[kind] = (RADIAL_HELPERS, r'''
    final distance = (position - center(size)).distance;
    final gap = spacing(size);
    final i = ((outer(size) - distance) / gap).round();
    if (i < 0 || i >= data.length || (distance - (outer(size) - i * gap)).abs() > gap * 0.4) return null;
    return i;
''', body.replace('__SWEEP__', sweep))

for kind in ['gauge', 'meter']:
    body = r'''
    final c = center(size), rr = radius(size), rect = Rect.fromCircle(center: c, radius: rr);
    canvas.drawArc(rect, math.pi, math.pi, false, stroke(ink.withValues(alpha: 0.08), rr * 0.2));
    final value = (data.first.value / 100).clamp(0, 1);
    canvas.drawArc(rect, math.pi, math.pi * value * progress, false, stroke(tone(0), rr * 0.2));
    label(canvas, '${_number(data.first.value)}%', c - const Offset(0, 28), color: text, centered: true, fontSize: 24);
    label(canvas, '0', c + Offset(-rr, 13), centered: true);
    label(canvas, '100', c + Offset(rr, 13), centered: true);
'''
    if kind == 'meter':
        body += r'''
    final angle = math.pi + math.pi * value * progress;
    final end = c + Offset(math.cos(angle), math.sin(angle)) * rr * 0.7;
    canvas.drawLine(c, end, stroke(ink, 3));
    canvas.drawCircle(c, 5, fill(ink));
'''
    else:
        body += r'''
    for (var i = 0; i <= 10; i++) {
      final a = math.pi + math.pi * i / 10;
      final vector = Offset(math.cos(a), math.sin(a));
      canvas.drawLine(c + vector * rr * 0.75, c + vector * rr * 0.8, stroke(ink.withValues(alpha: 0.35), 1.5));
    }
    canvas.drawCircle(c, 3, fill(ink.withValues(alpha: 0.2)));
'''
    PAINTERS[kind] = (r'''
  Offset center(Size size) => Offset(size.width / 2, size.height * 0.73);
  double radius(Size size) => math.min(size.width * 0.34, size.height * 0.56);
''', r'''
    final c = center(size), rr = radius(size), vector = position - c;
    return position.dy <= c.dy + 12 && vector.distance <= rr * 1.2 ? 0 : null;
''', body)

ROW_HELPERS = r'''
  List<Rect> rows(Size size) {
    final h = (size.height - 24) / data.length;
    return [for (var i = 0; i < data.length; i++) Rect.fromLTWH(14, 12 + i * h, size.width - 28, h - 6)];
  }
'''
HIT_ROWS = r'''
    final boxes = rows(size);
    for (var i = 0; i < boxes.length; i++) { if (boxes[i].contains(position)) return i; }
    return null;
'''
for kind in ['pyramid', 'funnel', 'bullet', 'sparkline']:
    body = r'''
    final boxes = rows(size);
    for (var i = 0; i < data.length; i++) {
      final d = data[i], r = boxes[i];
'''
    if kind in ['pyramid', 'funnel']:
        body += r'''
      final maxValue = math.max(1.0, data.map((d) => d.value).reduce(math.max));
      final width = r.width * (math.max(0, d.value) / maxValue).clamp(0, 1) * progress;
      final left = r.center.dx - width / 2;
      final box = RRect.fromRectAndRadius(Rect.fromLTWH(left, r.top, width, r.height), const Radius.circular(10));
      canvas.drawRRect(box, fill(tone(i)));
      if (selected == i) canvas.drawRRect(box, stroke(text, 1));
      label(canvas, '${d.label}  ${_number(d.value)}', Offset(r.center.dx, r.center.dy - 5),
        color: i < 2 ? (text == Colors.white ? Colors.black : Colors.white) : text, centered: true);
'''
    elif kind == 'bullet':
        body += r'''
      label(canvas, d.label, r.topLeft, color: text, fontSize: 10);
      label(canvas, '${_number(d.value)} / ${_number(d.target)}', Offset(r.right - 90, r.top), fontSize: 9);
      final maxValue = math.max(1.0, math.max(d.value.abs(), d.target.abs()) * 1.2);
      final bar = Rect.fromLTWH(r.left, r.top + r.height * 0.53, r.width, math.max(4, r.height * 0.28));
      canvas.drawRRect(RRect.fromRectAndRadius(bar, const Radius.circular(8)), fill(ink.withValues(alpha: 0.08)));
      final actual = Rect.fromLTWH(bar.left, bar.top, bar.width * (d.value / maxValue).clamp(0, 1) * progress, bar.height);
      canvas.drawRRect(RRect.fromRectAndRadius(actual, const Radius.circular(8)), fill(tone(0)));
      final targetX = bar.left + bar.width * (d.target / maxValue).clamp(0, 1);
      canvas.drawLine(Offset(targetX, bar.top - 3), Offset(targetX, bar.bottom + 3), stroke(text, 2));
'''
    else:
        body += r'''
      label(canvas, d.label, Offset(r.left, r.top + 4), color: text);
      label(canvas, _number(d.value), Offset(r.left, r.top + 20), color: text, fontSize: 14);
      final values = d.history.isEmpty ? [d.value] : d.history;
      final low = values.reduce(math.min), high = values.reduce(math.max);
      final span = math.max(0.01, high - low);
      final area = Rect.fromLTRB(r.left + r.width * 0.48, r.top + 5, r.right - 5, r.bottom - 5);
      final points = [for (var j = 0; j < values.length; j++) Offset(
        area.left + (values.length == 1 ? 0.5 : j / (values.length - 1)) * area.width,
        area.bottom - (values[j] - low) / span * area.height)];
      canvas.drawPath(curve(points), stroke(tone(0).withValues(alpha: progress), selected == i ? 3 : 2));
      canvas.drawCircle(points.last, 3, fill(ink));
'''
    body += '    }\n'
    PAINTERS[kind] = (ROW_HELPERS + (CURVE if kind == 'sparkline' else ''), HIT_ROWS, body)

PAINTERS['radar'] = (r'''
  Offset center(Size size) => Offset(size.width / 2, size.height / 2);
  double radius(Size size) => math.min(size.width * 0.32, size.height * 0.34);
  List<Offset> anchors(Size size) => [for (var i = 0; i < data.length; i++) center(size) +
    Offset(math.cos(-math.pi / 2 + i * math.pi * 2 / data.length), math.sin(-math.pi / 2 + i * math.pi * 2 / data.length)) * radius(size)];
''', NEAREST, r'''
    final c = center(size), anchorsList = anchors(size);
    for (var level = 1; level <= 4; level++) {
      final web = Path();
      for (var i = 0; i < data.length; i++) {
        final p = c + (anchorsList[i] - c) * (level / 4);
        if (i == 0) { web.moveTo(p.dx, p.dy); } else { web.lineTo(p.dx, p.dy); }
      }
      web.close();
      canvas.drawPath(web, stroke(text.withValues(alpha: 0.08), 1));
    }
    final polygon = Path();
    for (var i = 0; i < data.length; i++) {
      final a = anchorsList[i], p = c + (a - c) * (data[i].value / 100).clamp(0, 1) * progress;
      canvas.drawLine(c, a, stroke(text.withValues(alpha: 0.08), 1));
      if (i == 0) { polygon.moveTo(p.dx, p.dy); } else { polygon.lineTo(p.dx, p.dy); }
      label(canvas, data[i].label, c + (a - c) * 1.22 - const Offset(0, 4), centered: true, fontSize: 9);
      canvas.drawCircle(p, selected == i ? 5 : 3, fill(tone(0)));
    }
    polygon.close();
    canvas.drawPath(polygon, fill(ink.withValues(alpha: 0.15)));
    canvas.drawPath(polygon, stroke(ink, 2));
''')

PAINTERS['sankey'] = (ROW_HELPERS, HIT_ROWS, r'''
    final boxes = rows(size);
    final sink = Rect.fromLTWH(size.width * 0.73, size.height * 0.34, size.width * 0.23, size.height * 0.32);
    final total = math.max(1.0, data.fold<double>(0, (sum, d) => sum + math.max(0, d.value)));
    for (var i = 0; i < data.length; i++) {
      final row = boxes[i];
      final source = Rect.fromLTWH(row.left, row.top + row.height * 0.15, size.width * 0.27, row.height * 0.7);
      final path = Path()..moveTo(source.right, source.center.dy)
        ..cubicTo(size.width * 0.46, source.center.dy, size.width * 0.55, sink.center.dy, sink.left, sink.center.dy);
      final alpha = selected == null || selected == i ? 0.35 : 0.08;
      canvas.drawPath(path, stroke(ink.withValues(alpha: alpha),
        math.max(2.0, data[i].value / total * size.height * 0.24 * progress)));
      canvas.drawRRect(RRect.fromRectAndRadius(source, const Radius.circular(10)), fill(tone(i).withValues(alpha: 0.12)));
      label(canvas, data[i].label, source.topLeft + const Offset(6, 6), color: text, fontSize: 9);
      label(canvas, '${_number(data[i].value)}k', source.topLeft + const Offset(6, 21), fontSize: 9);
    }
    canvas.drawRRect(RRect.fromRectAndRadius(sink, const Radius.circular(14)), fill(ink));
    final inverse = text == Colors.white ? Colors.black : Colors.white;
    label(canvas, 'Leader Slot', Offset(sink.center.dx, sink.top + 10), centered: true, color: inverse, fontSize: 9);
    label(canvas, '${_number(total)}k', Offset(sink.center.dx, sink.top + 27), centered: true, color: inverse, fontSize: 15);
''')

PAINTERS['treemap'] = (r'''
  List<Rect> tiles(Size size) {
    final result = List<Rect>.filled(data.length, Rect.zero);
    void partition(List<int> indices, Rect r) {
      if (indices.isEmpty) return;
      if (indices.length == 1) { result[indices.first] = r.deflate(2); return; }
      final weights = [for (final i in indices) math.max(0.0, data[i].value)];
      final total = weights.fold<double>(0, (sum, v) => sum + v);
      var split = 1, first = weights.first;
      while (split < indices.length - 1 && first < total / 2) { first += weights[split++]; }
      final ratio = total <= 0 ? split / indices.length : (first / total).clamp(0.0, 1.0);
      if (r.width >= r.height) {
        final x = r.left + r.width * ratio;
        partition(indices.sublist(0, split), Rect.fromLTRB(r.left, r.top, x, r.bottom));
        partition(indices.sublist(split), Rect.fromLTRB(x, r.top, r.right, r.bottom));
      } else {
        final y = r.top + r.height * ratio;
        partition(indices.sublist(0, split), Rect.fromLTRB(r.left, r.top, r.right, y));
        partition(indices.sublist(split), Rect.fromLTRB(r.left, y, r.right, r.bottom));
      }
    }
    partition([for (var i = 0; i < data.length; i++) i], Rect.fromLTWH(10, 10, size.width - 20, size.height - 20));
    return result;
  }
''', r'''
    final boxes = tiles(size);
    for (var i = 0; i < boxes.length; i++) { if (boxes[i].contains(position)) return i; }
    return null;
''', r'''
    final boxes = tiles(size);
    for (var i = 0; i < data.length; i++) {
      final r = boxes[i];
      if (r.width < 1 || r.height < 1) continue;
      final rounded = RRect.fromRectAndRadius(r, const Radius.circular(12));
      canvas.drawRRect(rounded, fill(tone(i).withValues(alpha: (1 - i * 0.2).clamp(0.2, 1) * progress)));
      if (selected == i) canvas.drawRRect(rounded, stroke(text, 2));
      canvas.save();
      canvas.clipRect(r);
      final inverse = i < 2 ? (text == Colors.white ? Colors.black : Colors.white) : text;
      label(canvas, data[i].label, r.topLeft + const Offset(10, 10), color: inverse);
      label(canvas, '${_number(data[i].value)}%', r.topLeft + const Offset(10, 30), color: inverse, fontSize: 17);
      canvas.restore();
    }
''')

if __name__ == '__main__':
    generation()
