import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

const charts = <Widget>[
  MonoActivityHeatmap(),
  MonoRoundedLineChart(),
  MonoRoundedBarChart(),
  MonoRoundedAreaChart(),
  MonoRoundedDonutChart(),
  MonoRoundedComposedChart(),
  MonoRoundedScatterChart(),
  MonoRoundedCandlestickChart(),
  MonoRoundedKpiCardChart(),
  MonoRoundedPyramidChart(),
  MonoRoundedRadialBarGroup(),
  MonoRoundedGaugeArc(),
  MonoRoundedBulletChart(),
  MonoRoundedSankeyChart(),
  MonoRoundedStepChart(),
  MonoRoundedStackedBarChart(),
  MonoRoundedRadarChart(),
  MonoRoundedRadialGaugeChart(),
  MonoRoundedFunnelChart(),
  MonoRoundedHeatmapChart(),
  MonoRoundedSparklineChart(),
  MonoRoundedBubbleChart(),
  MonoRoundedTreemapChart(),
  MonoRoundedStreamChart(),
  MonoRoundedMeterChart(),
  MonoRoundedWaterfallChart(),
  MonoRoundedPolarChart(),
  MonoRoundedRangeChart(),
];

Widget host(
  Widget child, {
  Brightness brightness = Brightness.dark,
  double width = 420,
  bool reduced = false,
}) => MaterialApp(
  theme: ThemeData(brightness: brightness),
  home: MediaQuery(
    data: MediaQueryData(disableAnimations: reduced),
    child: Scaffold(
      body: Center(
        child: SizedBox(width: width, child: child),
      ),
    ),
  ),
);

Finder get stage => find.byWidgetPredicate((w) => w is CustomPaint && w.painter != null);

void main() {
  for (final brightness in Brightness.values) {
    testWidgets('all 28 charts paint on narrow and wide layouts in $brightness', (tester) async {
      for (final width in [280.0, 420.0]) {
        for (final chart in charts) {
          await tester.pumpWidget(host(chart, brightness: brightness, width: width));
          await tester.pumpAndSettle();
          expect(tester.takeException(), isNull, reason: '${chart.runtimeType} at $width');
          expect(stage, findsOneWidget, reason: '${chart.runtimeType} paints its data');
          await tester.pumpWidget(const SizedBox.shrink());
        }
      }
    });
  }

  testWidgets('custom data can be inspected by hover and tap; exiting clears selection', (tester) async {
    MonoRoundedLinePoint? selected;
    await tester.pumpWidget(
      host(
        MonoRoundedLineChart(
          animate: false,
          data: const [MonoRoundedLinePoint(label: 'Custom point', value: 25, secondary: 40)],
          onSelected: (value) => selected = value,
        ),
      ),
    );
    await tester.pump();
    final point = tester.getCenter(stage);
    final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
    await mouse.addPointer(location: Offset.zero);
    await mouse.moveTo(point);
    await tester.pump();
    expect(selected?.label, 'Custom point');
    expect(find.textContaining('Custom point: 25 / 40'), findsOneWidget);
    await mouse.moveTo(Offset.zero);
    await tester.pump();
    expect(selected, isNull);
    await tester.tapAt(point);
    await tester.pump();
    expect(selected?.value, 25);
    await tester.tapAt(point);
    await tester.pump();
    expect(selected, isNull);
    await mouse.removePointer();
  });

  testWidgets('changing dataset clears selection and updates the metric', (tester) async {
    MonoRoundedLinePoint? selected;
    await tester.pumpWidget(
      host(
        MonoRoundedLineChart(
          animate: false,
          datasets: const {
            'First': [MonoRoundedLinePoint(label: 'A', value: 10)],
            'Second': [MonoRoundedLinePoint(label: 'B', value: 70)],
          },
          onSelected: (value) => selected = value,
        ),
      ),
    );
    await tester.tapAt(tester.getCenter(stage));
    await tester.pump();
    expect(selected?.label, 'A');
    await tester.tap(find.byType(DropdownButton<String>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Second').last);
    await tester.pumpAndSettle();
    expect(find.text('70'), findsOneWidget);
    expect(selected, isNull);
    expect(find.textContaining('A: 10'), findsNothing);
  });

  testWidgets('empty data and non-finite observations display the empty state', (tester) async {
    for (final chart in [
      const MonoRoundedLineChart(data: []),
      const MonoRoundedLineChart(datasets: {}),
      const MonoRoundedLineChart(
        data: [MonoRoundedLinePoint(label: 'Invalid', value: double.nan)],
      ),
      const MonoRoundedScatterChart(
        data: [MonoRoundedScatterPoint(label: 'Invalid', value: 5, x: double.infinity)],
      ),
    ]) {
      await tester.pumpWidget(host(chart));
      await tester.pumpAndSettle();
      expect(find.text('No data'), findsNWidgets(2));
      expect(tester.takeException(), isNull);
    }
  });

  testWidgets('flat, negative and single-point data remain paintable', (tester) async {
    for (final chart in [
      const MonoRoundedLineChart(data: [MonoRoundedLinePoint(label: 'Flat', value: 0)]),
      const MonoRoundedRangeChart(data: [MonoRoundedRangePoint(label: 'Flat', value: 0, low: 0)]),
      const MonoRoundedWaterfallChart(
        data: [MonoRoundedWaterfallPoint(label: 'Expense', value: -20, base: 0)],
      ),
      const MonoRoundedDonutChart(data: [MonoRoundedDonutPoint(label: 'Zero', value: 0)]),
      const MonoRoundedTreemapChart(data: [MonoRoundedTreemapPoint(label: 'Zero', value: 0)]),
      const MonoRoundedSparklineChart(data: [MonoRoundedSparklinePoint(label: 'Flat', value: 0)]),
    ]) {
      await tester.pumpWidget(host(chart));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull, reason: '${chart.runtimeType} handles a degenerate domain');
    }
  });

  testWidgets('donut ignores its hole and identifies the correct segment', (tester) async {
    MonoRoundedDonutPoint? selected;
    await tester.pumpWidget(
      host(
        MonoRoundedDonutChart(
          animate: false,
          data: const [
            MonoRoundedDonutPoint(label: 'Half A', value: 50),
            MonoRoundedDonutPoint(label: 'Half B', value: 50),
          ],
          onSelected: (value) => selected = value,
        ),
      ),
    );
    final rect = tester.getRect(stage);
    await tester.tapAt(rect.center);
    expect(selected, isNull);
    await tester.tapAt(rect.center + Offset(rect.height * 0.34, 0));
    await tester.pump();
    expect(selected?.label, 'Half A');
    await tester.tapAt(rect.center - Offset(rect.height * 0.34, 0));
    await tester.pump();
    expect(selected?.label, 'Half B');
  });

  testWidgets('gauge preserves hundredths and respects reduced motion', (tester) async {
    await tester.pumpWidget(host(const MonoRoundedGaugeArc(), reduced: true));
    await tester.pump();
    expect(find.text('99.98'), findsOneWidget);
    expect(tester.binding.transientCallbackCount, 0);
    expect(tester.takeException(), isNull);
  });
}
