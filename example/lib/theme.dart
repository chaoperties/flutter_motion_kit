import 'package:flutter/material.dart';

/// Amicro's design language: Outfit type, a neutral "cement" palette, soft borders
/// instead of shadows, near-black dark mode and a cool off-white light mode.
class Tokens {
  const Tokens._({
    required this.page,
    required this.panel,
    required this.raised,
    required this.border,
    required this.text,
    required this.textMuted,
    required this.textFaint,
  });

  static const dark = Tokens._(
    page: Color(0xFF131313),
    panel: Color(0xFF181818),
    raised: Color(0xFF202020),
    border: Color(0xFF262626), // neutral-800
    text: Color(0xFFE3E3E3),
    textMuted: Color(0xFFA3A3A3), // neutral-400
    textFaint: Color(0xFF737373), // neutral-500
  );

  static const light = Tokens._(
    page: Color(0xFFF4F4F6),
    panel: Color(0xFFFFFFFF),
    raised: Color(0xFFF5F5F5), // neutral-100
    border: Color(0xFFE5E5E5), // neutral-200
    text: Color(0xFF171717),
    textMuted: Color(0xFF525252), // neutral-600
    textFaint: Color(0xFF737373), // neutral-500
  );

  final Color page;
  final Color panel;
  final Color raised;
  final Color border;
  final Color text;
  final Color textMuted;
  final Color textFaint;

  static Tokens of(BuildContext context) => Theme.of(context).brightness == Brightness.dark ? dark : light;
}

const monoFont = 'JetBrainsMono';

ThemeData buildTheme(Brightness brightness) {
  final t = brightness == Brightness.dark ? Tokens.dark : Tokens.light;
  final scheme = ColorScheme(
    brightness: brightness,
    primary: t.text,
    onPrimary: t.page,
    secondary: t.textMuted,
    onSecondary: t.page,
    error: const Color(0xFFF87171),
    onError: Colors.white,
    surface: t.page,
    onSurface: t.text,
    onSurfaceVariant: t.textMuted,
    surfaceContainerLowest: t.page,
    surfaceContainerLow: t.panel,
    surfaceContainer: t.panel,
    surfaceContainerHigh: t.raised,
    surfaceContainerHighest: t.raised,
    outline: t.border,
    outlineVariant: t.border,
  );
  final base = ThemeData(useMaterial3: true, colorScheme: scheme, fontFamily: 'Outfit');
  return base.copyWith(
    scaffoldBackgroundColor: t.page,
    dividerColor: t.border,
    dividerTheme: DividerThemeData(color: t.border, space: 1, thickness: 1),
    splashFactory: NoSplash.splashFactory,
    highlightColor: Colors.transparent,
    hoverColor: t.text.withValues(alpha: 0.04),
    textTheme: base.textTheme.apply(bodyColor: t.text, displayColor: t.text),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: t.raised,
      contentTextStyle: TextStyle(fontFamily: 'Outfit', color: t.text, fontSize: 13),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: t.border),
      ),
      elevation: 0,
      width: 260,
    ),
    tooltipTheme: TooltipThemeData(
      decoration: BoxDecoration(color: t.raised, borderRadius: BorderRadius.circular(8)),
      textStyle: TextStyle(fontFamily: 'Outfit', color: t.text, fontSize: 12),
    ),
  );
}
