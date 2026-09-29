import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_motion_kit/flutter_motion_kit.dart';

import 'demos.dart';
import 'theme.dart';

void main() => runApp(const GalleryApp());

class GalleryApp extends StatefulWidget {
  const GalleryApp({super.key});

  @override
  State<GalleryApp> createState() => _GalleryAppState();
}

class _GalleryAppState extends State<GalleryApp> {
  ThemeMode _mode = ThemeMode.dark;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'flutter_motion_kit',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light),
      darkTheme: buildTheme(Brightness.dark),
      themeMode: _mode,
      home: GalleryHome(
        dark: _mode == ThemeMode.dark,
        onToggleTheme: () =>
            setState(() => _mode = _mode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark),
      ),
    );
  }
}

class GalleryHome extends StatefulWidget {
  const GalleryHome({super.key, required this.dark, required this.onToggleTheme});

  final bool dark;
  final VoidCallback onToggleTheme;

  @override
  State<GalleryHome> createState() => _GalleryHomeState();
}

class _GalleryHomeState extends State<GalleryHome> {
  int _selected = 0;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final sidebar = _Sidebar(
      selected: _selected,
      dark: widget.dark,
      onToggleTheme: widget.onToggleTheme,
      onSelect: (i) {
        setState(() => _selected = i);
        if (!wide) Navigator.of(context).maybePop();
      },
    );
    final page = DemoPage(key: ValueKey(_selected), demo: demos[_selected]);

    if (wide) {
      return Scaffold(
        body: Row(
          children: [
            Container(
              width: 248,
              decoration: BoxDecoration(
                border: Border(right: BorderSide(color: t.border)),
              ),
              child: sidebar,
            ),
            Expanded(child: page),
          ],
        ),
      );
    }
    return Scaffold(
      appBar: AppBar(
        backgroundColor: t.page,
        surfaceTintColor: Colors.transparent,
        scrolledUnderElevation: 0,
        shape: Border(bottom: BorderSide(color: t.border)),
        title: Text(demos[_selected].name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
      ),
      drawer: Drawer(backgroundColor: t.page, shape: const RoundedRectangleBorder(), child: sidebar),
      body: page,
    );
  }
}

class _Sidebar extends StatelessWidget {
  const _Sidebar({
    required this.selected,
    required this.onSelect,
    required this.dark,
    required this.onToggleTheme,
  });

  final int selected;
  final ValueChanged<int> onSelect;
  final bool dark;
  final VoidCallback onToggleTheme;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    final items = <Widget>[];
    String? category;
    for (var i = 0; i < demos.length; i++) {
      if (demos[i].category != category) {
        category = demos[i].category;
        items.add(
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 20, 12, 6),
            child: Text(
              category.toUpperCase(),
              style: TextStyle(
                fontSize: 11,
                letterSpacing: 1.1,
                fontWeight: FontWeight.w500,
                color: t.textFaint,
              ),
            ),
          ),
        );
      }
      items.add(_NavItem(label: demos[i].name, selected: i == selected, onTap: () => onSelect(i)));
    }

    return SafeArea(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
            child: Row(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(color: t.text, borderRadius: BorderRadius.circular(8)),
                  alignment: Alignment.center,
                  child: Text(
                    'm',
                    style: TextStyle(color: t.page, fontWeight: FontWeight.w700, fontSize: 16),
                  ),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'motion kit',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: t.text),
                    ),
                    Text('for Flutter', style: TextStyle(fontSize: 12, color: t.textFaint)),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(padding: const EdgeInsets.symmetric(horizontal: 8), children: items),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: MotionButton(
              label: dark ? 'Dark' : 'Light',
              icon: dark ? Icons.dark_mode_outlined : Icons.light_mode_outlined,
              icon2: dark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
              icon2Color: dark ? const Color(0xFFFACC15) : null,
              effect: MotionButtonEffect.morph,
              onPressed: onToggleTheme,
            ),
          ),
        ],
      ),
    );
  }
}

class _NavItem extends StatefulWidget {
  const _NavItem({required this.label, required this.selected, required this.onTap});

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  State<_NavItem> createState() => _NavItemState();
}

class _NavItemState extends State<_NavItem> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          margin: const EdgeInsets.symmetric(vertical: 1),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: widget.selected
                ? t.raised
                : (_hover ? t.text.withValues(alpha: 0.03) : Colors.transparent),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            widget.label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: widget.selected ? FontWeight.w500 : FontWeight.w400,
              color: widget.selected || _hover ? t.text : t.textMuted,
            ),
          ),
        ),
      ),
    );
  }
}

class DemoPage extends StatefulWidget {
  const DemoPage({super.key, required this.demo});

  final Demo demo;

  @override
  State<DemoPage> createState() => _DemoPageState();
}

class _DemoPageState extends State<DemoPage> {
  bool _showCode = false;
  int _run = 0;

  @override
  Widget build(BuildContext context) {
    final demo = widget.demo;
    final t = Tokens.of(context);
    final narrow = MediaQuery.sizeOf(context).width < 600;

    return SingleChildScrollView(
      padding: EdgeInsets.symmetric(horizontal: narrow ? 16 : 40, vertical: narrow ? 20 : 36),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1080),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                demo.category.toUpperCase(),
                style: TextStyle(
                  fontSize: 11,
                  letterSpacing: 1.1,
                  fontWeight: FontWeight.w500,
                  color: t.textFaint,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                demo.name,
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.6,
                  color: t.text,
                ),
              ),
              const SizedBox(height: 8),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 640),
                child: Text(
                  demo.description,
                  style: TextStyle(fontSize: 15, height: 1.5, color: t.textMuted),
                ),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  if (demo.source != null) _Pill(text: 'lib/widgets/${demo.source}', mono: true),
                  const _Pill(text: 'Zero dependencies'),
                  const _Pill(text: 'Web · Mobile · Desktop'),
                ],
              ),
              const SizedBox(height: 28),
              if (demo.tiles != null)
                _TileGrid(tiles: demo.tiles!, layout: demo.tileLayout)
              else ...[
                Row(
                  children: [
                    _Segmented(
                      labels: const ['Preview', 'Code'],
                      index: _showCode ? 1 : 0,
                      onChanged: (i) => setState(() => _showCode = i == 1),
                    ),
                    const Spacer(),
                    if (!_showCode)
                      _GhostButton(
                        icon: Icons.replay_rounded,
                        label: 'Replay',
                        onTap: () => setState(() => _run++),
                      ),
                  ],
                ),
                const SizedBox(height: 14),
                if (_showCode)
                  SizedBox(
                    height: 560,
                    child: CodeView(assetPath: demo.assetPath, fileName: demo.source!),
                  )
                else
                  _PreviewStage(
                    hint: demo.hint,
                    // Keyed by run count so Replay remounts the demo and restarts its animation.
                    child: KeyedSubtree(key: ValueKey(_run), child: demo.builder!(context)),
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _PreviewStage extends StatelessWidget {
  const _PreviewStage({required this.child, this.hint});

  final Widget child;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    return Container(
      constraints: const BoxConstraints(minHeight: 460),
      decoration: BoxDecoration(
        color: t.panel,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: t.border),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Positioned.fill(child: CustomPaint(painter: _DotGridPainter(t.text.withValues(alpha: 0.05)))),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 48),
            child: Center(child: child),
          ),
          if (hint != null)
            Positioned(
              left: 18,
              bottom: 14,
              child: Text(hint!, style: TextStyle(fontSize: 12, color: t.textFaint)),
            ),
        ],
      ),
    );
  }
}

class _DotGridPainter extends CustomPainter {
  _DotGridPainter(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color;
    for (double x = 12; x < size.width; x += 24) {
      for (double y = 12; y < size.height; y += 24) {
        canvas.drawCircle(Offset(x, y), 1, paint);
      }
    }
  }

  @override
  bool shouldRepaint(_DotGridPainter old) => old.color != color;
}

class _TileGrid extends StatelessWidget {
  const _TileGrid({required this.tiles, required this.layout});

  final List<DemoTile> tiles;
  final TileLayout layout;

  @override
  Widget build(BuildContext context) {
    final stage = layout == TileLayout.stage;
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: stage ? 540 : 230,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: stage ? 1.45 : 1.05,
      ),
      itemCount: tiles.length,
      itemBuilder: (context, i) => _Tile(tile: tiles[i], stage: stage),
    );
  }
}

class _Tile extends StatefulWidget {
  const _Tile({required this.tile, required this.stage});

  final DemoTile tile;

  /// Scale the preview into a fixed stage and keep clicks for the preview itself.
  final bool stage;

  @override
  State<_Tile> createState() => _TileState();
}

class _TileState extends State<_Tile> {
  bool _hover = false;

  void _openCode() {
    showDialog<void>(
      context: context,
      barrierColor: Colors.black.withValues(alpha: 0.5),
      builder: (context) {
        final t = Tokens.of(context);
        return Dialog(
          backgroundColor: t.page,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: BorderSide(color: t.border),
          ),
          insetPadding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 820, maxHeight: 640),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 12, 12),
                  child: Row(
                    children: [
                      Text(
                        widget.tile.name,
                        style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(width: 16),
                      if (!widget.stage)
                        SizedBox(height: 24, child: Center(child: widget.tile.builder(context))),
                      const Spacer(),
                      IconButton(
                        tooltip: 'Close',
                        onPressed: () => Navigator.pop(context),
                        icon: Icon(Icons.close_rounded, color: t.textMuted, size: 20),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                    child: CodeView(assetPath: widget.tile.assetPath, fileName: widget.tile.source),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    final tile = widget.tile;
    Widget preview = tile.hoverBuilder != null ? tile.hoverBuilder!(_hover) : tile.builder(context);
    if (widget.stage) {
      // Every layout gets the same 580x320 stage, scaled down to fit the tile.
      preview = Padding(
        padding: const EdgeInsets.only(bottom: 28),
        child: FittedBox(
          fit: BoxFit.scaleDown,
          child: SizedBox(width: 580, height: 320, child: Center(child: preview)),
        ),
      );
    }
    return MouseRegion(
      cursor: widget.stage ? MouseCursor.defer : SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.stage ? null : _openCode,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          clipBehavior: Clip.antiAlias,
          decoration: BoxDecoration(
            color: t.panel,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: _hover ? t.textFaint.withValues(alpha: 0.6) : t.border),
          ),
          child: Stack(
            children: [
              Positioned.fill(child: Center(child: preview)),
              Positioned(
                left: 14,
                right: 8,
                bottom: 8,
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        widget.tile.name,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 13, color: _hover ? t.text : t.textMuted),
                      ),
                    ),
                    AnimatedOpacity(
                      // Stage tiles have no click-to-open, so keep their buttons discoverable.
                      opacity: _hover ? 1 : (widget.stage ? 0.45 : 0),
                      duration: const Duration(milliseconds: 150),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (widget.stage)
                            IconButton(
                              tooltip: 'View code',
                              visualDensity: VisualDensity.compact,
                              onPressed: _openCode,
                              icon: Icon(Icons.code_rounded, size: 16, color: t.textMuted),
                            ),
                          _CopyIcon(assetPath: widget.tile.assetPath, fileName: widget.tile.source),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Copies a source asset to the clipboard; the icon briefly turns into a check.
class _CopyIcon extends StatefulWidget {
  const _CopyIcon({required this.assetPath, required this.fileName});

  final String assetPath;
  final String fileName;

  @override
  State<_CopyIcon> createState() => _CopyIconState();
}

class _CopyIconState extends State<_CopyIcon> {
  bool _done = false;

  Future<void> _copy() async {
    final code = await rootBundle.loadString(widget.assetPath);
    await Clipboard.setData(ClipboardData(text: code));
    if (!mounted) return;
    setState(() => _done = true);
    await Future<void>.delayed(const Duration(milliseconds: 1400));
    if (mounted) setState(() => _done = false);
  }

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    return IconButton(
      tooltip: 'Copy ${widget.fileName.split('/').last}',
      visualDensity: VisualDensity.compact,
      onPressed: _copy,
      icon: AnimatedSwitcher(
        duration: const Duration(milliseconds: 200),
        transitionBuilder: (child, a) => ScaleTransition(scale: a, child: child),
        child: _done
            ? const Icon(Icons.check_rounded, key: ValueKey(1), size: 16, color: Color(0xFF34D399))
            : Icon(Icons.copy_rounded, key: const ValueKey(0), size: 16, color: t.textMuted),
      ),
    );
  }
}

class CodeView extends StatefulWidget {
  const CodeView({super.key, required this.assetPath, required this.fileName});

  final String assetPath;
  final String fileName;

  @override
  State<CodeView> createState() => _CodeViewState();
}

class _CodeViewState extends State<CodeView> {
  late final Future<String> _source = rootBundle.loadString(widget.assetPath);

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    return Container(
      decoration: BoxDecoration(
        color: t.panel,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: t.border),
      ),
      clipBehavior: Clip.antiAlias,
      child: FutureBuilder<String>(
        future: _source,
        builder: (context, snap) {
          if (snap.hasError) {
            return Center(
              child: Text(
                'Source not found. Run: dart run tool/sync_sources.dart',
                style: TextStyle(color: t.textMuted),
              ),
            );
          }
          if (!snap.hasData) return const Center(child: IOSSpinner());
          final code = snap.data!;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.fromLTRB(16, 8, 8, 8),
                decoration: BoxDecoration(
                  border: Border(bottom: BorderSide(color: t.border)),
                ),
                child: Row(
                  children: [
                    Text(
                      widget.fileName.split('/').last,
                      style: TextStyle(fontFamily: monoFont, fontSize: 12, color: t.textMuted),
                    ),
                    const Spacer(),
                    MotionButton(
                      label: 'Copy',
                      activeLabel: 'Copied',
                      icon: Icons.copy_rounded,
                      icon2: Icons.check_rounded,
                      icon2Color: const Color(0xFF34D399),
                      trigger: MotionButtonTrigger.press,
                      onPressed: () => Clipboard.setData(ClipboardData(text: code)),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(18),
                  child: SelectableText(
                    code,
                    style: TextStyle(fontFamily: monoFont, fontSize: 12.5, height: 1.6, color: t.text),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Segmented extends StatelessWidget {
  const _Segmented({required this.labels, required this.index, required this.onChanged});

  final List<String> labels;
  final int index;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    const w = 92.0;
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: t.raised,
        borderRadius: BorderRadius.circular(40),
        border: Border.all(color: t.border),
      ),
      child: Stack(
        children: [
          AnimatedPositioned(
            duration: const Duration(milliseconds: 320),
            curve: Curves.easeOutBack,
            left: index * w,
            top: 0,
            bottom: 0,
            width: w,
            child: Container(
              decoration: BoxDecoration(
                color: t.panel,
                borderRadius: BorderRadius.circular(40),
                border: Border.all(color: t.border),
              ),
            ),
          ),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var i = 0; i < labels.length; i++)
                MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => onChanged(i),
                    child: SizedBox(
                      width: w,
                      height: 30,
                      child: Center(
                        child: AnimatedDefaultTextStyle(
                          duration: const Duration(milliseconds: 200),
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: i == index ? t.text : t.textFaint,
                          ),
                          child: Text(labels[i]),
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({required this.text, this.mono = false});

  final String text;
  final bool mono;

  @override
  Widget build(BuildContext context) {
    final t = Tokens.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: t.raised,
        borderRadius: BorderRadius.circular(40),
        border: Border.all(color: t.border),
      ),
      child: Text(
        text,
        style: TextStyle(fontSize: 12, color: t.textMuted, fontFamily: mono ? monoFont : null),
      ),
    );
  }
}

class _GhostButton extends StatelessWidget {
  const _GhostButton({required this.icon, required this.label, required this.onTap});

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return MotionButton(label: label, icon: icon, effect: MotionButtonEffect.rotate, onPressed: onTap);
  }
}
