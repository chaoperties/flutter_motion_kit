import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_motion_kit_example/demos.dart';
import 'package:flutter_motion_kit_example/main.dart';
import 'package:flutter_test/flutter_test.dart';

/// Loaders animate forever, so pumpAndSettle never settles. Instead: let real async
/// work (asset loading) finish, then run enough frames for any transition to complete.
Future<void> settle(WidgetTester tester) async {
  await tester.pump();
  await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 50)));
  await tester.pump(const Duration(milliseconds: 600));
  await tester.pump(const Duration(milliseconds: 600));
}

void main() {
  test('every demo source asset is synced and up to date', () {
    final sources = [
      for (final demo in demos) ...[
        if (demo.source != null) (demo.assetPath, demo.source!),
        for (final tile in demo.tiles ?? const <DemoTile>[]) (tile.assetPath, tile.source),
      ],
    ];
    for (final (asset, source) in sources) {
      final file = File(asset);
      expect(file.existsSync(), isTrue, reason: '$asset missing — run dart run tool/sync_sources.dart');
      expect(
        file.readAsStringSync(),
        File('../lib/widgets/$source').readAsStringSync(),
        reason: '$source changed — run dart run tool/sync_sources.dart',
      );
    }
  });

  testWidgets('every demo renders, and its code can be opened', (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const GalleryApp());
    for (final demo in demos) {
      await tester.tap(find.text(demo.name).first);
      await settle(tester);
      expect(find.text(demo.description), findsOneWidget);

      if (demo.tiles != null) {
        expect(find.text(demo.tiles!.first.name), findsOneWidget);
        if (demo.tileLayout != TileLayout.small) {
          // These tiles keep clicks for the preview, so code opens from the tile's code button.
          await tester.tap(find.byTooltip('View code').first);
        } else {
          await tester.tap(find.text(demo.tiles!.first.name));
        }
        await settle(tester);
        expect(find.textContaining("import 'package:flutter/material.dart';"), findsOneWidget);
        await tester.tap(find.byTooltip('Close'));
        await settle(tester);
      } else {
        await tester.tap(find.text('Code'));
        await settle(tester);
        expect(find.textContaining("import 'package:flutter/material.dart';"), findsOneWidget);
        await tester.tap(find.text('Preview'));
        await settle(tester);
      }
    }
  });

  testWidgets('theme toggle switches to light mode', (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const GalleryApp());
    expect(Theme.of(tester.element(find.byType(GalleryHome))).brightness, Brightness.dark);
    await tester.tap(find.text('Dark'));
    await settle(tester);
    expect(Theme.of(tester.element(find.byType(GalleryHome))).brightness, Brightness.light);
  });
}
