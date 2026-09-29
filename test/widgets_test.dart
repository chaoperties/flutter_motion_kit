import 'package:flutter/material.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Widget child) => MaterialApp(
  home: Scaffold(body: Center(child: child)),
);

List<Widget> _cards(int n) => [
  for (var i = 0; i < n; i++)
    Container(key: ValueKey('card$i'), width: 100, height: 140, color: Colors.primaries[i]),
];

void main() {
  testWidgets('ArcFan fans out on tap and back again', (tester) async {
    await tester.pumpWidget(_app(ArcFan(children: _cards(5))));
    final before = tester.getCenter(find.byKey(const ValueKey('card0')));

    await tester.tap(find.byType(ArcFan));
    await tester.pumpAndSettle();
    final after = tester.getCenter(find.byKey(const ValueKey('card0')));
    expect(after.dx, lessThan(before.dx), reason: 'first card should swing left');

    await tester.tap(find.byType(ArcFan));
    await tester.pumpAndSettle();
    expect(tester.getCenter(find.byKey(const ValueKey('card0'))).dx, closeTo(before.dx, 0.5));
  });

  testWidgets('ArcFan follows the expanded prop', (tester) async {
    await tester.pumpWidget(_app(ArcFan(expanded: false, children: _cards(3))));
    final closed = tester.getCenter(find.byKey(const ValueKey('card2')));
    await tester.pumpWidget(_app(ArcFan(expanded: true, children: _cards(3))));
    await tester.pumpAndSettle();
    expect(tester.getCenter(find.byKey(const ValueKey('card2'))).dx, greaterThan(closed.dx));
  });

  testWidgets('LinearSpread lays cards out in a row', (tester) async {
    await tester.pumpWidget(_app(LinearSpread(expanded: true, spacing: 110, children: _cards(3))));
    await tester.pumpAndSettle();
    final xs = [for (var i = 0; i < 3; i++) tester.getCenter(find.byKey(ValueKey('card$i'))).dx];
    expect(xs[1] - xs[0], closeTo(110, 0.5));
    expect(xs[2] - xs[1], closeTo(110, 0.5));
  });

  testWidgets('FadeUp ends fully visible after its delay', (tester) async {
    await tester.pumpWidget(
      _app(const FadeUp(delay: Duration(milliseconds: 200), blur: true, child: Text('hi'))),
    );
    Opacity opacity() => tester.widget(find.ancestor(of: find.text('hi'), matching: find.byType(Opacity)));
    expect(opacity().opacity, 0);
    await tester.pump(const Duration(milliseconds: 200));
    await tester.pumpAndSettle();
    expect(opacity().opacity, 1);
  });

  testWidgets('FadeUp disposed before its delay does not throw', (tester) async {
    await tester.pumpWidget(_app(const FadeUp(delay: Duration(seconds: 1), child: Text('hi'))));
    await tester.pumpWidget(_app(const SizedBox()));
    await tester.pump(const Duration(seconds: 2));
  });

  testWidgets('CoverFlow: tap and drag change the centred item', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(
      _app(
        CoverFlow(
          itemCount: 6,
          itemBuilder: (_, i) => ColoredBox(color: Colors.primaries[i], child: Text('item$i')),
          onChanged: changes.add,
        ),
      ),
    );

    // Item 1 is partly hidden behind item 0; tap its visible right side.
    await tester.tapAt(tester.getCenter(find.byType(CoverFlow)) + const Offset(120, 0));
    await tester.pumpAndSettle();
    expect(changes.last, 1);

    await tester.drag(find.byType(CoverFlow), const Offset(-400, 0));
    await tester.pumpAndSettle();
    expect(changes.last, greaterThan(1));

    // Can't scroll past the end.
    await tester.drag(find.byType(CoverFlow), const Offset(-5000, 0));
    await tester.pumpAndSettle();
    expect(changes.last, 5);
  });
}
