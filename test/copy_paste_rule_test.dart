// Every file in lib/widgets must be copyable on its own: it may import only
// dart: libraries and package:flutter/, never another file in this kit or a
// third-party package.
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  final files = Directory('lib/widgets')
      .listSync(recursive: true)
      .whereType<File>()
      .where((f) => f.path.endsWith('.dart'))
      .toList();

  test('there are widgets to check', () => expect(files, isNotEmpty));

  for (final file in files) {
    test('${file.path} imports only dart: and package:flutter/', () {
      final imports = RegExp(
        r'''^\s*(?:import|export|part)\s+['"]([^'"]+)['"]''',
        multiLine: true,
      ).allMatches(file.readAsStringSync()).map((m) => m.group(1)!);
      final bad = imports.where((u) => !u.startsWith('dart:') && !u.startsWith('package:flutter/'));
      expect(bad, isEmpty, reason: 'Widget files must be self-contained so they can be copied alone.');
    });
  }
}
