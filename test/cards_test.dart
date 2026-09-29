import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Widget child, {Brightness brightness = Brightness.dark}) => MaterialApp(
  theme: ThemeData(brightness: brightness),
  home: Scaffold(body: Center(child: child)),
);

List<Widget> _cards(int n) => [for (var i = 0; i < n; i++) SizedBox.expand(key: ValueKey('c$i'))];

/// Every hover layout, built with keyed children so each card can be located.
final _layouts = <String, (int, Widget Function(bool? hovered, double intensity))>{
  'CardArc': (5, (h, k) => CardArc(hovered: h, intensity: k, children: _cards(5))),
  'CardArc.seven': (7, (h, k) => CardArc.seven(hovered: h, intensity: k, children: _cards(7))),
  'CardArc.long': (5, (h, k) => CardArc.long(hovered: h, intensity: k, children: _cards(5))),
  'CardLinearSpread': (5, (h, k) => CardLinearSpread(hovered: h, intensity: k, children: _cards(5))),
  'CardCornerFan': (5, (h, k) => CardCornerFan(hovered: h, intensity: k, children: _cards(5))),
  'CardStampArc': (5, (h, k) => CardStampArc(hovered: h, intensity: k, children: _cards(5))),
  'CardStampArc colorful': (
    5,
    (h, k) => CardStampArc(hovered: h, intensity: k, colorful: true, children: _cards(5)),
  ),
  'CardCascadeStagger': (5, (h, k) => CardCascadeStagger(hovered: h, intensity: k, children: _cards(5))),
  'CardScatterSpread': (5, (h, k) => CardScatterSpread(hovered: h, intensity: k, children: _cards(5))),
  'CardWheelFan': (5, (h, k) => CardWheelFan(hovered: h, intensity: k, children: _cards(5))),
};

void main() {
  List<Offset> centres(WidgetTester tester, int n) => [
    for (var i = 0; i < n; i++) tester.getCenter(find.byKey(ValueKey('c$i'))),
  ];

  for (final MapEntry(key: name, value: (n, build)) in _layouts.entries) {
    testWidgets('$name spreads when hovered and restacks when not', (tester) async {
      await tester.pumpWidget(_app(build(false, 1)));
      final stacked = centres(tester, n);

      await tester.pumpWidget(_app(build(true, 1)));
      await tester.pumpAndSettle();
      final spread = centres(tester, n);
      final moved = [for (var i = 0; i < n; i++) (spread[i] - stacked[i]).distance];
      expect(moved.where((d) => d > 5).length, greaterThanOrEqualTo(n - 1), reason: 'cards should fan out');

      await tester.pumpWidget(_app(build(false, 1)));
      await tester.pumpAndSettle();
      final back = centres(tester, n);
      for (var i = 0; i < n; i++) {
        expect((back[i] - stacked[i]).distance, lessThan(0.5), reason: 'card $i returns to the pile');
      }
    });

    testWidgets('$name with intensity 0 barely moves', (tester) async {
      await tester.pumpWidget(_app(build(false, 0)));
      final stacked = centres(tester, n);
      await tester.pumpWidget(_app(build(true, 0)));
      await tester.pumpAndSettle();
      final spread = centres(tester, n);
      for (var i = 0; i < n; i++) {
        // Only the centre card's small scale-up remains.
        expect((spread[i] - stacked[i]).distance, lessThan(8));
      }
    });
  }

  testWidgets('hover layouts follow the mouse when uncontrolled', (tester) async {
    await tester.pumpWidget(_app(CardLinearSpread(children: _cards(5))));
    final before = tester.getCenter(find.byKey(const ValueKey('c0')));
    final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
    await mouse.addPointer(location: Offset.zero);
    addTearDown(mouse.removePointer);
    await mouse.moveTo(tester.getCenter(find.byType(CardLinearSpread)));
    await tester.pumpAndSettle();
    expect(tester.getCenter(find.byKey(const ValueKey('c0'))).dx, lessThan(before.dx - 30));
    await mouse.moveTo(const Offset(1, 1));
    await tester.pumpAndSettle();
    expect(tester.getCenter(find.byKey(const ValueKey('c0'))).dx, closeTo(before.dx, 0.5));
  });

  testWidgets('hover layouts toggle on touch taps', (tester) async {
    await tester.pumpWidget(_app(CardWheelFan(children: _cards(5))));
    final before = tester.getCenter(find.byKey(const ValueKey('c0')));
    await tester.tap(find.byType(CardWheelFan));
    await tester.pumpAndSettle();
    expect((tester.getCenter(find.byKey(const ValueKey('c0'))) - before).distance, greaterThan(10));
    await tester.tap(find.byType(CardWheelFan));
    await tester.pumpAndSettle();
    expect((tester.getCenter(find.byKey(const ValueKey('c0'))) - before).distance, lessThan(0.5));
  });

  testWidgets('default placeholder cards render in both themes', (tester) async {
    for (final b in Brightness.values) {
      await tester.pumpWidget(
        _app(
          const Wrap(
            children: [
              CardArc(hovered: true),
              CardArc.seven(),
              CardStampArc(colorful: true, hovered: true),
              CardCornerFan(),
            ],
          ),
          brightness: b,
        ),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    }
  });

  testWidgets('CardCarousel: dots, arrows and keys change the centred card', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(_app(SizedBox(width: 520, child: CardCarousel(onChanged: changes.add))));
    await tester.tap(find.bySemanticsLabel('Next'));
    await tester.pumpAndSettle();
    expect(changes.last, 3);
    // Only the neighbours are on stage (as in Amicro); tap the one on the left.
    await tester.tap(find.text('3'));
    await tester.pumpAndSettle();
    expect(changes.last, 2);
    expect(find.text('Card 3'), findsOneWidget);

    for (var i = 0; i < 3; i++) {
      await tester.tap(find.bySemanticsLabel('Previous'));
      await tester.pumpAndSettle();
    }
    expect(changes.last, 0, reason: 'clamped at the first card');
    expect(changes.where((c) => c == 0).length, 1, reason: 'no repeat notification when clamped');

    Focus.of(tester.element(find.text('Card 1'))).requestFocus();
    await tester.pump();
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowRight);
    await tester.pumpAndSettle();
    expect(changes.last, 1);
  });

  testWidgets('CardCarousel tilts when hovered', (tester) async {
    await tester.pumpWidget(_app(const SizedBox(width: 520, child: CardCarousel(hovered: false))));
    final before = tester.getCenter(find.text('1'));
    await tester.pumpWidget(_app(const SizedBox(width: 520, child: CardCarousel(hovered: true))));
    await tester.pumpAndSettle();
    expect((tester.getCenter(find.text('1')) - before).distance, greaterThan(10));
  });

  testWidgets('CardCoverFlow: tapping a side card brings it to the centre', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(_app(CardCoverFlow(onChanged: changes.add)));
    await tester.tap(find.bySemanticsLabel('Next'));
    await tester.pumpAndSettle();
    expect(changes.last, 3);
    await tester.tap(find.bySemanticsLabel('Next'));
    await tester.tap(find.bySemanticsLabel('Next'));
    await tester.pumpAndSettle();
    expect(changes.last, 4, reason: 'clamped at the last card');
    expect(tester.takeException(), isNull);
  });

  testWidgets('CardTimeMachine: hovering the timeline travels back in time', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(_app(CardTimeMachine(onChanged: changes.add)));
    final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
    await mouse.addPointer(location: Offset.zero);
    addTearDown(mouse.removePointer);

    await mouse.moveTo(tester.getCenter(find.bySemanticsLabel('1w ago')));
    await tester.pumpAndSettle();
    expect(changes.last, 2);
    expect(find.text('1w ago'), findsOneWidget, reason: 'hovered tick shows its label');

    await mouse.moveTo(const Offset(1, 1));
    await tester.pumpAndSettle();
    expect(find.text('1w ago'), findsNothing);

    await tester.tap(find.bySemanticsLabel('1y ago'));
    await tester.pumpAndSettle();
    expect(changes.last, 4);
  });

  testWidgets('CardTimeMachine: arrow keys step through time', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(_app(CardTimeMachine(onChanged: changes.add, framed: false)));
    Focus.of(tester.element(find.bySemanticsLabel('Today'))).requestFocus();
    await tester.pump();
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowDown);
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowDown);
    await tester.pumpAndSettle();
    expect(changes.last, 2);
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowUp);
    await tester.pumpAndSettle();
    expect(changes.last, 1);
  });
}
