import 'dart:ui' show Tristate;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

import 'toggle_widgets.g.dart';

Widget _app(Widget child, {Brightness brightness = Brightness.dark}) => MaterialApp(
  theme: ThemeData(brightness: brightness),
  home: Scaffold(
    body: Center(
      child: RepaintBoundary(key: const ValueKey('shot'), child: child),
    ),
  ),
);

/// The pixels of the widget under test, so any visual change can be detected.
Future<Uint8List> _shot(WidgetTester tester) async {
  final element = tester.element(find.byKey(const ValueKey('shot')));
  final bytes = await tester.runAsync(() async {
    final image = await captureImage(element);
    final data = await image.toByteData();
    image.dispose();
    return data!.buffer.asUint8List();
  });
  return bytes!;
}

bool _toggled(WidgetTester tester) {
  final ours = find.descendant(of: find.byKey(const ValueKey('shot')), matching: find.byType(Semantics)).first;
  return tester.getSemantics(ours).flagsCollection.isToggled == Tristate.isTrue;
}

void main() {
  for (final MapEntry(key: name, value: build) in toggleWidgets.entries) {
    testWidgets('$name toggles on tap by itself and settles', (tester) async {
      final changes = <bool>[];
      await tester.pumpWidget(_app(build(null, changes.add)));
      final off = await _shot(tester);
      expect(_toggled(tester), isFalse);

      await tester.tap(find.byKey(const ValueKey('shot')));
      await tester.pumpAndSettle();
      expect(changes, [true]);
      expect(_toggled(tester), isTrue);
      final on = await _shot(tester);
      expect(on, isNot(off));

      await tester.tap(find.byKey(const ValueKey('shot')));
      await tester.pumpAndSettle();
      expect(changes, [true, false]);
      // Move the pointer away so hover colours don't count as a difference.
      await tester.pumpWidget(_app(build(null, changes.add)));
      await tester.pumpAndSettle();
      expect(await _shot(tester), off, reason: 'back exactly where it started');
    });

    testWidgets('$name follows value when controlled', (tester) async {
      final changes = <bool>[];
      await tester.pumpWidget(_app(build(false, changes.add)));
      final off = await _shot(tester);
      await tester.tap(find.byKey(const ValueKey('shot')));
      await tester.pumpAndSettle();
      expect(changes, [true]);
      expect(_toggled(tester), isFalse, reason: 'the parent has not changed value yet');

      await tester.pumpWidget(_app(build(true, changes.add)));
      await tester.pumpAndSettle();
      expect(_toggled(tester), isTrue);
      expect(await _shot(tester), isNot(off));
    });

    testWidgets('$name works from the keyboard and in light mode', (tester) async {
      final changes = <bool>[];
      await tester.pumpWidget(_app(build(null, changes.add), brightness: Brightness.light));
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pump();
      await tester.sendKeyEvent(LogicalKeyboardKey.space);
      await tester.pumpAndSettle();
      expect(changes, [true]);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('LikeToggle and RepostToggle count the user in', (tester) async {
    await tester.pumpWidget(
      _app(
        const Row(
          mainAxisSize: MainAxisSize.min,
          children: [LikeToggle(count: 42), RepostToggle(count: 18, initialValue: true)],
        ),
      ),
    );
    expect(find.text('42'), findsOneWidget);
    expect(find.text('19'), findsOneWidget);
    await tester.tap(find.text('42'));
    await tester.tap(find.text('19'));
    await tester.pumpAndSettle();
    expect(find.text('43'), findsOneWidget);
    expect(find.text('18'), findsOneWidget);
  });

  testWidgets('BookmarkToggle swaps its label', (tester) async {
    await tester.pumpWidget(_app(const BookmarkToggle()));
    await tester.tap(find.text('Bookmark'));
    await tester.pumpAndSettle();
    expect(find.text('Saved'), findsOneWidget);
  });

  testWidgets('PillTabs: taps, arrow keys and a pill that follows', (tester) async {
    final changes = <int>[];
    await tester.pumpWidget(_app(PillTabs(onChanged: changes.add)));
    final start = await _shot(tester);

    await tester.tap(find.text('Monthly'));
    await tester.pumpAndSettle();
    expect(changes, [2]);
    expect(await _shot(tester), isNot(start));

    Focus.of(tester.element(find.text('Monthly'))).requestFocus();
    await tester.pump();
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowLeft);
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowLeft);
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowLeft);
    await tester.pumpAndSettle();
    expect(changes, [2, 1, 0], reason: 'stops at the first tab');
    expect(await _shot(tester), start);
  });

  testWidgets('PillTabs follows index when controlled', (tester) async {
    await tester.pumpWidget(_app(const PillTabs(tabs: ['A', 'Bee'], index: 0)));
    final a = await _shot(tester);
    await tester.pumpWidget(_app(const PillTabs(tabs: ['A', 'Bee'], index: 1)));
    await tester.pumpAndSettle();
    expect(await _shot(tester), isNot(a));
    expect(tester.getSemantics(find.text('Bee')).flagsCollection.isSelected, Tristate.isTrue);
  });
}
