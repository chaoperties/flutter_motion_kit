// Copies every widget file from ../lib/widgets into assets/sources so the
// gallery can show (and copy) the exact source. Run after editing a widget:
//
//   dart run tool/sync_sources.dart
//
// Files are saved as .dart.txt so the analyzer doesn't treat them as code.
import 'dart:io';

void main() {
  final src = Directory('../lib/widgets');
  final out = Directory('assets/sources');
  if (out.existsSync()) out.deleteSync(recursive: true);

  var count = 0;
  for (final file in src.listSync(recursive: true).whereType<File>()) {
    if (!file.path.endsWith('.dart')) continue;
    final rel = file.path.substring(src.path.length + 1).replaceAll(r'\', '/');
    final target = File('${out.path}/$rel.txt')..createSync(recursive: true);
    target.writeAsStringSync(file.readAsStringSync());
    count++;
  }
  stdout.writeln('Synced $count widget sources into ${out.path}');
}
