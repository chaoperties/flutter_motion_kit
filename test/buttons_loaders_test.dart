import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Widget child, {Brightness brightness = Brightness.dark}) => MaterialApp(
  theme: ThemeData(brightness: brightness),
  home: Scaffold(body: Center(child: child)),
);

const _loaders = <Widget>[
  PulseDots(),
  BounceDots(),
  WaveDots(),
  GridDots(),
  TypingIndicator(),
  DotsRing(),
  ClassicSpinner(),
  IOSSpinner(),
  CometSpinner(),
  ArcTracer(),
  DualArc(),
  OrbitingDot(),
  RippleEffect(),
  BouncingBars(),
  BarCascade(),
  Equalizer(),
  FlipSquare(),
  NewtonsCradle(),
  SquareSpinner(),
  TextShimmer(),
];

void main() {
  for (final brightness in Brightness.values) {
    testWidgets('all loaders animate without errors ($brightness)', (tester) async {
      await tester.pumpWidget(_app(Wrap(children: _loaders), brightness: brightness));
      // Step through more than one full loop of the slowest loader.
      for (var i = 0; i < 30; i++) {
        await tester.pump(const Duration(milliseconds: 90));
      }
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('loaders accept a custom colour and duration change', (tester) async {
    await tester.pumpWidget(_app(const PulseDots(color: Colors.red)));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pumpWidget(_app(const PulseDots(color: Colors.red, duration: Duration(milliseconds: 500))));
    await tester.pump(const Duration(milliseconds: 300));
    expect(tester.takeException(), isNull);
  });

  for (final (effect, trigger) in [
    for (final e in MotionButtonEffect.values)
      for (final t in MotionButtonTrigger.values) (e, t),
  ]) {
    testWidgets('MotionButton $effect ($trigger): hover in and out, then press', (tester) async {
      var pressed = 0;
      await tester.pumpWidget(
        _app(
          MotionButton(
            label: 'Go',
            icon: Icons.add,
            icon2: Icons.check,
            activeLabel: 'Done',
            effect: effect,
            onPressed: () => pressed++,
          ),
        ),
      );

      final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
      await mouse.addPointer(location: Offset.zero);
      addTearDown(mouse.removePointer);
      await mouse.moveTo(tester.getCenter(find.byType(MotionButton)));
      await tester.pump(const Duration(milliseconds: 200));
      await mouse.moveTo(tester.getCenter(find.byType(MotionButton)) + const Offset(10, 5));
      await tester.pump(const Duration(milliseconds: 600));
      await mouse.moveTo(const Offset(1, 1));
      await tester.pumpAndSettle();

      await tester.tap(find.byType(MotionButton));
      await tester.pumpAndSettle();
      expect(pressed, 1);
      expect(tester.takeException(), isNull);
    });
  }

  Future<TestGesture> hoverOver(WidgetTester tester, Finder finder) async {
    final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
    await mouse.addPointer(location: Offset.zero);
    addTearDown(mouse.removePointer);
    await mouse.moveTo(tester.getCenter(finder));
    await tester.pumpAndSettle();
    return mouse;
  }

  testWidgets('hover trigger: activeLabel shows on hover, lingers, then reverts', (tester) async {
    await tester.pumpWidget(
      _app(const MotionButton(label: 'Open', activeLabel: 'Go!', icon: Icons.open_in_new)),
    );
    final mouse = await hoverOver(tester, find.byType(MotionButton));
    expect(find.text('Go!'), findsOneWidget);
    await mouse.moveTo(const Offset(1, 1));
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.text('Go!'), findsOneWidget, reason: 'lingers for stayActive');
    await tester.pumpAndSettle(const Duration(milliseconds: 100));
    expect(find.text('Open'), findsOneWidget);
  });

  testWidgets('press trigger: hovering never claims "Copied"; clicking does, then reverts', (tester) async {
    var copies = 0;
    await tester.pumpWidget(
      _app(
        MotionButton(
          label: 'Copy',
          activeLabel: 'Copied',
          icon: Icons.copy,
          icon2: Icons.check,
          trigger: MotionButtonTrigger.press,
          onPressed: () => copies++,
        ),
      ),
    );

    final mouse = await hoverOver(tester, find.byType(MotionButton));
    expect(find.text('Copy'), findsOneWidget);
    expect(find.text('Copied'), findsNothing);
    expect(find.byIcon(Icons.check), findsNothing);

    await mouse.down(tester.getCenter(find.byType(MotionButton)));
    await mouse.up();
    await tester.pump(const Duration(milliseconds: 400));
    expect(copies, 1);
    expect(find.text('Copied'), findsOneWidget);
    expect(find.byIcon(Icons.check), findsOneWidget);

    // Still hovered, but the confirmation expires after confirmDuration.
    await tester.pump(const Duration(milliseconds: 1200));
    await tester.pumpAndSettle();
    expect(find.text('Copy'), findsOneWidget);
    expect(find.byIcon(Icons.check), findsNothing);
  });

  testWidgets('press trigger: clicking again restarts the confirmation', (tester) async {
    await tester.pumpWidget(
      _app(
        const MotionButton(
          label: 'Copy',
          activeLabel: 'Copied',
          icon: Icons.copy,
          trigger: MotionButtonTrigger.press,
          confirmDuration: Duration(milliseconds: 1000),
        ),
      ),
    );
    await tester.tap(find.byType(MotionButton));
    await tester.pump(const Duration(milliseconds: 800));
    await tester.tap(find.byType(MotionButton));
    await tester.pump(const Duration(milliseconds: 800));
    expect(find.text('Copied'), findsOneWidget, reason: 'second press extended it');
    await tester.pumpAndSettle();
    expect(find.text('Copy'), findsOneWidget);
  });

  testWidgets('press trigger confirms from the keyboard too', (tester) async {
    await tester.pumpWidget(
      _app(
        const MotionButton(
          label: 'Save',
          activeLabel: 'Saved',
          icon: Icons.bookmark_border,
          trigger: MotionButtonTrigger.press,
        ),
      ),
    );
    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await tester.pump();
    expect(find.text('Saved'), findsNothing, reason: 'focus alone must not confirm');
    await tester.sendKeyEvent(LogicalKeyboardKey.enter);
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Saved'), findsOneWidget);
    await tester.pumpAndSettle();
  });

  testWidgets('MotionButton activates from the keyboard', (tester) async {
    var pressed = 0;
    await tester.pumpWidget(_app(MotionButton(label: 'Go', icon: Icons.add, onPressed: () => pressed++)));
    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await tester.pump();
    await tester.sendKeyEvent(LogicalKeyboardKey.enter);
    await tester.pumpAndSettle();
    expect(pressed, 1);
  });
}
