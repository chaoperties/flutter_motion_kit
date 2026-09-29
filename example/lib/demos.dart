import 'package:flutter/material.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';

import 'card_catalog.g.dart';
import 'loader_catalog.g.dart';
import 'theme.dart';

/// A small live preview inside a collection page, with its own source file.
class DemoTile {
  const DemoTile({required this.name, required this.source, required this.builder}) : hoverBuilder = null;

  /// A tile whose preview reacts to the pointer being anywhere over the tile.
  DemoTile.hover({required this.name, required this.source, required Widget Function(bool hovered) builder})
    : builder = ((_) => builder(false)),
      hoverBuilder = builder;

  final String name;
  final String source;
  final WidgetBuilder builder;
  final Widget Function(bool hovered)? hoverBuilder;

  String get assetPath => 'assets/sources/$source.txt';
}

/// One page in the gallery: either a single widget ([builder] + [source]) or a
/// collection of small widgets shown as a grid of [tiles].
class Demo {
  const Demo({
    required this.name,
    required this.category,
    required this.description,
    this.source,
    this.builder,
    this.tiles,
    this.hint,
    this.tileLayout = TileLayout.small,
  }) : assert((builder != null && source != null) || tiles != null);

  final String name;
  final String category;
  final String description;

  /// Path of the widget file, relative to lib/widgets.
  final String? source;
  final WidgetBuilder? builder;
  final List<DemoTile>? tiles;

  /// How to interact with the preview, shown under it.
  final String? hint;

  final TileLayout tileLayout;

  String get assetPath => 'assets/sources/$source.txt';
}

/// How a collection page lays out its tiles.
enum TileLayout {
  /// Small tiles; clicking a tile opens its code.
  small,

  /// Two wide tiles per row, previews scaled to fit a fixed stage. The previews are
  /// interactive, so code opens from the tile's code button rather than a tile click.
  stage,
}

const _yellow = Color(0xFFFACC15);
const _blue = Color(0xFF60A5FA);
const _emerald = Color(0xFF34D399);
const _pink = Color(0xFFEC4899);
const _red = Color(0xFFF87171);
const _orange = Color(0xFFFB923C);

List<Widget> buttonShowcase() => const [
  MotionButton(
    label: 'Download for Mac',
    icon: Icons.apple,
    icon2: Icons.arrow_forward_rounded,
    effect: MotionButtonEffect.slideArrow,
  ),
  MotionButton(
    label: 'Star on GitHub',
    icon: Icons.code_rounded,
    icon2: Icons.star_rounded,
    icon2Color: _yellow,
    effect: MotionButtonEffect.sparkle,
  ),
  MotionButton(
    label: 'Deploy App',
    icon: Icons.cloud_outlined,
    icon2: Icons.cloud_upload_outlined,
    icon2Color: _blue,
    effect: MotionButtonEffect.morph,
  ),
  MotionButton(
    label: 'Copy Hash',
    activeLabel: 'Copied',
    icon: Icons.copy_rounded,
    icon2: Icons.check_rounded,
    icon2Color: _emerald,
    effect: MotionButtonEffect.morph,
    // Copy, Like and Save report a result, so they confirm on press instead of on hover.
    trigger: MotionButtonTrigger.press,
  ),
  MotionButton(
    label: 'Like',
    activeLabel: 'Liked',
    icon: Icons.favorite_border_rounded,
    icon2: Icons.favorite_rounded,
    iconColor: _pink,
    effect: MotionButtonEffect.pulse,
    trigger: MotionButtonTrigger.press,
  ),
  MotionButton(
    label: 'Save',
    activeLabel: 'Saved',
    icon: Icons.bookmark_border_rounded,
    icon2: Icons.bookmark_rounded,
    icon2Color: _yellow,
    effect: MotionButtonEffect.morph,
    trigger: MotionButtonTrigger.press,
  ),
  MotionButton(
    label: 'Share',
    icon: Icons.link_rounded,
    icon2: Icons.send_rounded,
    icon2Color: _blue,
    effect: MotionButtonEffect.morph,
  ),
  MotionButton(label: 'Settings', icon: Icons.settings_outlined, effect: MotionButtonEffect.rotate),
  MotionButton(
    label: 'Delete',
    icon: Icons.delete_outline_rounded,
    iconColor: _red,
    effect: MotionButtonEffect.shake,
  ),
  MotionButton(
    label: 'Subscribe',
    icon: Icons.notifications_none_rounded,
    icon2: Icons.notifications_active_outlined,
    icon2Color: _orange,
    effect: MotionButtonEffect.ring,
  ),
  MotionButton(
    label: 'Theme',
    icon: Icons.dark_mode_outlined,
    icon2: Icons.light_mode_outlined,
    icon2Color: _yellow,
    effect: MotionButtonEffect.morph,
  ),
  MotionButton(
    label: 'Unlock',
    icon: Icons.lock_outline_rounded,
    icon2: Icons.lock_open_rounded,
    icon2Color: _emerald,
    effect: MotionButtonEffect.morph,
  ),
  MotionButton(label: 'Glare Shine', icon: Icons.auto_awesome_outlined, effect: MotionButtonEffect.glare),
  MotionButton(label: 'Text Reveal', icon: Icons.add_rounded, effect: MotionButtonEffect.textReveal),
  MotionButton(label: 'Magnetic Field', icon: Icons.explore_outlined, effect: MotionButtonEffect.magnetic),
  MotionButton(label: 'Expand Ring', icon: Icons.adjust_rounded, effect: MotionButtonEffect.expandRing),
];

final demos = <Demo>[
  Demo(
    name: 'Motion Button',
    category: 'Buttons',
    source: 'buttons/motion_button.dart',
    description:
        'A pill button with eleven micro-interactions: icon morphs, sparkles, shakes, glare, '
        'magnetic pull and more. Decorative effects play on hover; result effects like '
        '"Copied" wait for the click (trigger: press).',
    hint: 'Hover to preview · Copy, Like and Save confirm only when clicked',
    builder: (_) => Padding(
      padding: const EdgeInsets.all(32),
      child: Wrap(spacing: 14, runSpacing: 18, alignment: WrapAlignment.center, children: buttonShowcase()),
    ),
  ),
  Demo(
    name: 'Loaders',
    category: 'Loaders',
    description:
        '${loaderCatalog.length} loading indicators — dots, rings, bars, shapes and text. '
        'Each one is its own file; copy only the ones you need.',
    tiles: [for (final l in loaderCatalog) DemoTile(name: l.name, source: l.source, builder: l.builder)],
  ),
  Demo(
    name: 'Card Layouts',
    category: 'Cards',
    description:
        "All twelve of Amicro's card layouts. Hover a tile to spread its cards; the carousels "
        'and Time Machine are clickable. Each layout is one file.',
    tileLayout: TileLayout.stage,
    tiles: [
      for (final c in hoverCardCatalog) DemoTile.hover(name: c.name, source: c.source, builder: c.builder),
      DemoTile.hover(
        name: 'Carousel',
        source: 'cards/card_carousel.dart',
        builder: (hovered) => CardCarousel(hovered: hovered),
      ),
      DemoTile(
        name: 'Cover Flow',
        source: 'cards/card_cover_flow.dart',
        builder: (_) => const CardCoverFlow(),
      ),
      DemoTile(
        name: 'Time Machine',
        source: 'cards/card_time_machine.dart',
        builder: (_) => const CardTimeMachine(),
      ),
    ],
  ),
  Demo(
    name: 'Arc Fan',
    category: 'Cards',
    source: 'cards/arc_fan.dart',
    description:
        'A stack of cards that fans out along an arc, one after another. '
        'Hovering a card while open pops it up.',
    hint: 'Hover or tap the stack',
    builder: (_) => ArcFan(children: [for (var i = 0; i < 7; i++) DemoCard(index: i)]),
  ),
  Demo(
    name: 'Linear Spread',
    category: 'Cards',
    source: 'cards/linear_spread.dart',
    description: 'A messy pile of cards that slides out into a neat row, centre cards first.',
    hint: 'Hover or tap the pile',
    builder: (_) => LinearSpread(
      spacing: 92,
      children: [for (var i = 0; i < 5; i++) DemoCard(index: i, size: const Size(84, 118))],
    ),
  ),
  Demo(
    name: 'Cover Flow',
    category: 'Carousels',
    source: 'carousels/cover_flow.dart',
    description: 'A 3D carousel with spring physics. The centre item faces you, neighbours turn away.',
    hint: 'Drag, tap a side item, or use the arrow keys',
    builder: (_) => CoverFlow(
      itemCount: 10,
      itemSize: const Size(160, 210),
      itemBuilder: (_, i) => DemoCard(index: i, size: const Size(160, 210), elevated: false),
    ),
  ),
  Demo(
    name: 'Fade Up',
    category: 'Transitions',
    source: 'transitions/fade_up.dart',
    description:
        'Fades a widget in as it drifts up into place. Stagger siblings with a delay; '
        'set blur for a focus-pull entrance.',
    hint: 'Press Replay to see it again',
    builder: (_) => Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 0; i < 4; i++)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 5),
            child: FadeUp(
              delay: Duration(milliseconds: 90 * i),
              blur: true,
              child: DemoListTile(index: i),
            ),
          ),
      ],
    ),
  ),
];

/// A monochrome placeholder card in Amicro's style: tonal surface, hairline border, faux content.
class DemoCard extends StatelessWidget {
  const DemoCard({super.key, required this.index, this.size = const Size(110, 156), this.elevated = true});

  final int index;
  final Size size;
  final bool elevated;

  static const _icons = [
    Icons.music_note_rounded,
    Icons.photo_outlined,
    Icons.bolt_rounded,
    Icons.map_outlined,
    Icons.star_outline_rounded,
    Icons.coffee_outlined,
    Icons.flight_outlined,
    Icons.palette_outlined,
    Icons.headphones_outlined,
    Icons.eco_outlined,
  ];

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final t = Tokens.of(context);
    // Alternate a few neutral tones so stacked cards stay readable.
    final tone = index % 3;
    final top = dark
        ? [const Color(0xFF2A2A2A), const Color(0xFF262626), const Color(0xFF303030)][tone]
        : [const Color(0xFFFFFFFF), const Color(0xFFFAFAFA), const Color(0xFFF5F5F5)][tone];
    final bottom = dark ? const Color(0xFF1C1C1E) : const Color(0xFFEDEDF0);
    final line = t.text.withValues(alpha: dark ? 0.16 : 0.1);

    return Container(
      width: size.width,
      height: size.height,
      padding: EdgeInsets.all(size.width * 0.11),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [top, bottom],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
        borderRadius: BorderRadius.circular(size.width * 0.13),
        border: Border.all(color: dark ? const Color(0xFF2C2C2E) : const Color(0xFFD1D1D6)),
        boxShadow: elevated
            ? [
                // Soft enough that a pile of seven cards doesn't build up a dark band.
                BoxShadow(
                  color: Colors.black.withValues(alpha: dark ? 0.35 : 0.04),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(_icons[index % _icons.length], size: size.width * 0.16, color: t.textMuted),
              const Spacer(),
              Text(
                '${index + 1}'.padLeft(2, '0'),
                style: TextStyle(fontSize: size.width * 0.1, color: t.textFaint, fontWeight: FontWeight.w500),
              ),
            ],
          ),
          const Spacer(),
          _bar(size.width * 0.55, line),
          SizedBox(height: size.width * 0.05),
          _bar(size.width * 0.35, line.withValues(alpha: line.a * 0.6)),
        ],
      ),
    );
  }

  Widget _bar(double width, Color color) => Container(
    height: 5,
    width: width,
    decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3)),
  );
}

class DemoListTile extends StatelessWidget {
  const DemoListTile({super.key, required this.index});

  final int index;

  static const _rows = [
    (Icons.layers_outlined, 'Design tokens', 'Colour, type, radius'),
    (Icons.animation_rounded, 'Motion presets', 'Springs and curves'),
    (Icons.style_outlined, 'Card layouts', 'Fans, stacks, carousels'),
    (Icons.content_copy_rounded, 'Copy & paste', 'One file, no dependencies'),
  ];

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    final (icon, title, subtitle) = _rows[index % _rows.length];
    return Container(
      width: 320,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: t.panel,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: t.border),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(color: t.raised, borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, size: 18, color: t.textMuted),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: t.text),
                ),
                Text(
                  subtitle,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: t.textFaint),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
