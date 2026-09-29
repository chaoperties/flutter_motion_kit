import 'dart:typed_data';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

import 'text_widgets.g.dart';

Widget _app(
  Widget child, {
  Brightness brightness = Brightness.dark,
  bool reduceMotion = false,
}) => MaterialApp(
  theme: ThemeData(brightness: brightness),
  home: MediaQuery(
    data: MediaQueryData(disableAnimations: reduceMotion),
    child: Scaffold(
      body: Center(
        child: RepaintBoundary(key: const ValueKey('shot'), child: child),
      ),
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

/// All the text the widget shows, however it was split up.
String _shown(WidgetTester tester) => tester
    .widgetList<Text>(find.byType(Text))
    .map((t) => t.data!)
    .join()
    .replaceAll(' ', ' ')
    .replaceAll(' ', '');

void main() {
  for (final MapEntry(key: name, value: (kind, _, build))
      in textWidgets.entries) {
    testWidgets('$name renders all of its text in both themes', (tester) async {
      for (final b in Brightness.values) {
        await tester.pumpWidget(_app(build('Hi there you'), brightness: b));
        await tester.pump(const Duration(seconds: 3));
        expect(_shown(tester), 'Hithereyou');
        expect(find.bySemanticsLabel('Hi there you'), findsOneWidget);
        expect(tester.takeException(), isNull);
      }
    });

    switch (kind) {
      case TextKind.enter:
        testWidgets('$name animates in and then comes to rest', (tester) async {
          await tester.pumpWidget(_app(build('Hello')));
          await tester.pump(const Duration(milliseconds: 16));
          final early = await _shot(tester);
          await tester.pump(const Duration(seconds: 3));
          final done = await _shot(tester);
          expect(
            early,
            isNot(done),
            reason: 'the first frame should differ from the final one',
          );
          expect(
            tester.binding.hasScheduledFrame,
            isFalse,
            reason: 'no frames once finished',
          );

          // A new text plays the animation again.
          await tester.pumpWidget(_app(build('Hellp')));
          await tester.pump(const Duration(milliseconds: 16));
          expect(tester.binding.hasScheduledFrame, isTrue);
          await tester.pump(const Duration(seconds: 3));
        });

        testWidgets('$name shows its final state at once with reduced motion', (
          tester,
        ) async {
          await tester.pumpWidget(_app(build('Hello')));
          await tester.pump(const Duration(seconds: 3));
          final done = await _shot(tester);
          await tester.pumpWidget(_app(build('Hello'), reduceMotion: true));
          await tester.pumpWidget(
            _app(
              KeyedSubtree(key: UniqueKey(), child: build('Hello')),
              reduceMotion: true,
            ),
          );
          expect(await _shot(tester), done);
          await tester.pump(const Duration(seconds: 3));
        });
      case TextKind.loop:
        testWidgets('$name keeps moving', (tester) async {
          await tester.pumpWidget(_app(build('Hello')));
          await tester.pump(const Duration(milliseconds: 200));
          final a = await _shot(tester);
          await tester.pump(const Duration(milliseconds: 500));
          expect(await _shot(tester), isNot(a));
          expect(tester.binding.hasScheduledFrame, isTrue);
        });
      case TextKind.hover:
        testWidgets('$name reacts to the pointer and settles back', (
          tester,
        ) async {
          await tester.pumpWidget(_app(build('Hello')));
          final rest = await _shot(tester);
          final mouse = await tester.createGesture(
            kind: PointerDeviceKind.mouse,
          );
          await mouse.addPointer(location: Offset.zero);
          addTearDown(mouse.removePointer);

          await mouse.moveTo(tester.getCenter(find.byType(Text).first));
          await tester.pumpAndSettle();
          expect(await _shot(tester), isNot(rest));

          await mouse.moveTo(Offset.zero);
          await tester.pumpAndSettle();
          expect(await _shot(tester), rest);
        });
    }
  }

  testWidgets(
    'characters are split by grapheme, so Thai and emoji stay whole',
    (tester) async {
      final (_, _, build) = textWidgets['FadeInChar']!;
      await tester.pumpWidget(_app(build('น้ำ 👍🏽')));
      await tester.pump(const Duration(seconds: 3));
      final units = tester
          .widgetList<Text>(find.byType(Text))
          .map((t) => t.data)
          .toList();
      expect(units, ['น้ำ', ' ', '👍🏽']);
    },
  );

  testWidgets('delay holds the animation back', (tester) async {
    await tester.pumpWidget(
      _app(const FadeInText('Hello', delay: Duration(milliseconds: 500))),
    );
    await tester.pump(const Duration(milliseconds: 16));
    final start = await _shot(tester);
    await tester.pump(const Duration(milliseconds: 400));
    expect(
      await _shot(tester),
      start,
      reason: 'still invisible during the delay',
    );
    await tester.pump(const Duration(milliseconds: 400));
    expect(await _shot(tester), isNot(start));
    await tester.pump(const Duration(seconds: 3));
  });
}
