# flutter_motion_kit

[![CI](https://github.com/chaoperties/flutter_motion_kit/actions/workflows/ci.yml/badge.svg)](https://github.com/chaoperties/flutter_motion_kit/actions/workflows/ci.yml)

Copy-paste micro-interactions for Flutter — card fans, 3D carousels, text
animations, toggles, loaders and entrance transitions. Inspired by [Amicro](https://github.com/Subhan-code/Amicro--Micro-transitions-)
(React + Motion), rebuilt on Flutter's own animation engine.

**Every widget is a single file that imports only Flutter.** Copy the file into
your app and it works — no package to install, and you own the code.

| Widget | File | What it does |
|---|---|---|
| `MotionButton` | `lib/widgets/buttons/motion_button.dart` | Pill button with 11 hover effects (morph, sparkle, shake, glare, magnetic…) |
| 20 loaders | `lib/widgets/loaders/*.dart` | Dots, rings, bars, shapes and text — one file each |
| 45 text animations | `lib/widgets/text/*.dart` | Amicro's text effects: reveals, slides, springs, 3D flips, distortion, hover and loops — `BlurUpChar('Hello')` |
| 13 toggles | `lib/widgets/toggles/*.dart` | Amicro's toggles: 8 switches (Double Bounce, Solid, Rectangle, Circle, Classic, Morph, Checkmark, Theme), Bookmark/Like/Dislike/Repost actions and `PillTabs` — self-managed, or controlled with `value` + `onChanged` |
| 28 mono charts | `lib/widgets/charts/*.dart` | 30 previews: rounded line/area/bar charts, donut, gauges, radar, heatmaps, candlesticks, Sankey, treemap and more — hover/tap to inspect data |
| 12 card layouts | `lib/widgets/cards/card_*.dart` | Amicro's cards: Arc (5/7/long), Linear Spread, Corner Fan, Stamp Arc, Cascade Stagger, Scatter Spread, Wheel Fan, Carousel, Cover Flow, Time Machine |
| `ArcFan` | `lib/widgets/cards/arc_fan.dart` | Stack of cards that fans out along an arc |
| `LinearSpread` | `lib/widgets/cards/linear_spread.dart` | Messy pile that slides into a neat row |
| `CoverFlow` | `lib/widgets/carousels/cover_flow.dart` | 3D carousel with spring physics |
| `FadeUp` | `lib/widgets/transitions/fade_up.dart` | Fade + drift-up entrance, optional blur |

Widgets follow the ambient light/dark theme and default to Amicro's neutral
palette; every colour can be overridden. `MotionButton`, the loaders, the text animations,
the toggles and the `Card*` layouts are ports of Amicro components (MIT) — see `THIRD_PARTY_NOTICES.md`.

## Use it

**Copy (recommended):** open the gallery, pick a widget, press **Copy**, paste
into your project. Or copy the file from `lib/widgets/` directly.

**Or as a dependency:**

```yaml
dependencies:
  flutter_motion_kit:
    path: ../flutter_motion_kit   # or a git url
```

```dart
import 'package:flutter_motion_kit/flutter_motion_kit.dart';
```

## Gallery

[Open the live gallery](https://chaoperties.github.io/flutter_motion_kit/).
GitHub Actions builds and deploys the example to GitHub Pages on every push to `main`.

```bash
cd example
flutter run -d chrome
```

## Mono charts

Open **Mono Charts** in the gallery to preview all 30 examples, inspect values,
switch datasets and copy any chart's standalone Dart file. Charts follow the
ambient light/dark theme and respect reduced-motion settings.

```dart
MonoRoundedLineChart(
  unit: 'ms',
  data: const [
    MonoRoundedLinePoint(label: 'Mon', value: 124, secondary: 155),
    MonoRoundedLinePoint(label: 'Tue', value: 132, secondary: 158),
    MonoRoundedLinePoint(label: 'Wed', value: 158, secondary: 172),
  ],
  onSelected: (point) => debugPrint(point?.label),
)
```

Each chart exposes typed points, `data` for one series, `datasets` for named
series, `unit`, `width`, `height`, colour overrides and `onSelected`. Default
values are demo data. For financial candles, `value` is the closing price; for
range bands it is the upper bound. `secondary` and `tertiary` supply additional
series, while scatter/bubble points use `x`, `value` (y) and `size`.

To update generated charts, edit `tool/gen_mono_charts.py` or
`tool/mono_chart.dart.tmpl`, then regenerate and sync the copyable sources:

```bash
python tool/gen_mono_charts.py
dart format --line-length 110 lib/widgets/charts example/lib/mono_chart_catalog.g.dart
cd example
dart run tool/sync_sources.dart
```

## Adding a loader

Loaders are generated so each file can stay standalone without hand-copying
boilerplate. Add an entry to `LOADERS` in `tool/gen_loaders.py`, then:

```bash
python tool/gen_loaders.py             # writes lib/widgets/loaders/, exports, gallery catalogue
cd example && dart run tool/sync_sources.dart
```

## Adding a text animation

Text animations are generated too: add an entry to `EFFECTS` in `tool/gen_text.py` (a pose
such as `opacity=(0, 1), y=(15, 0)` plus a timing), run `python tool/gen_text.py`, then sync
the gallery sources. Character effects split by grapheme, so Thai and emoji stay whole.

## Adding a toggle

Switches and action buttons are generated from `SWITCHES` / `ACTIONS` in
`tool/gen_toggles.py` (`PillTabs` is hand-written). Run `python tool/gen_toggles.py`, then sync
the gallery sources.

## Adding a hover card layout

The nine hover layouts share one spring-driven mechanism and are generated the same way:
add an entry to `LAYOUTS` in `tool/gen_cards.py`, run `python tool/gen_cards.py`, then sync
the gallery sources.

## Adding a widget

1. Create `lib/widgets/<category>/<name>.dart`. It may import only `dart:*` and
   `package:flutter/*` — `test/copy_paste_rule_test.dart` enforces this.
2. Start the file with a comment: what it does, a usage snippet, how to interact.
3. Export it from `lib/flutter_motion_kit.dart` and add a test in `test/widgets_test.dart`.
4. Add a `Demo` entry in `example/lib/demos.dart` (and the asset folder to
   `example/pubspec.yaml` if it's a new category).
5. Run `dart run tool/sync_sources.dart` in `example/` so the gallery shows the new source.
