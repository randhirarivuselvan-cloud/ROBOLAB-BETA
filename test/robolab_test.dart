import 'package:flutter_test/flutter_test.dart';
import 'package:robolab/main.dart';

void main() {
  testWidgets('RoboLab app starts', (tester) async {
    await tester.pumpWidget(const RoboLabApp());
    expect(find.text('RoboLab'), findsWidgets);
    expect(find.text('Build something real.'), findsOneWidget);
  });
}
