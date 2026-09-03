import '../models/project.dart';

class RoboLabEngine {
  const RoboLabEngine();

  RoboProject run(String prompt, {String name = 'RoboLab Project', String id = 'local'}) {
    final normalized = prompt.trim();
    final requirements = _requirements(normalized);
    final components = _components(normalized);
    final architecture = _architecture(normalized, components);
    final connections = _connections(normalized, components);
    final warnings = _warnings(normalized, components);
    final code = _firmware(normalized, components);
    final verification = _verify(normalized, components, connections, code, warnings);

    final passed = verification.every((r) => r.ok);
    return RoboProject(
      id: id,
      name: name,
      prompt: normalized,
      stage: passed ? ProjectStage.ready : ProjectStage.verification,
      requirements: requirements,
      components: components,
      architecture: architecture,
      connections: connections,
      generatedCode: code,
      warnings: warnings,
      verification: verification,
    );
  }

  List<String> _requirements(String text) {
    final t = text.toLowerCase();
    final result = <String>[];
    if (t.contains('line') && (t.contains('follow') || t.contains('follower'))) result.add('Detect and follow a line using reflected-light sensing.');
    if (t.contains('obstacle') || t.contains('avoid')) result.add('Detect obstacles and respond without unsafe uncontrolled motion.');
    if (t.contains('bluetooth')) result.add('Provide short-range wireless control/status.');
    if (t.contains('wifi')) result.add('Provide network connectivity for telemetry or control.');
    if (t.contains('servo')) result.add('Control one or more servo actuators.');
    if (t.contains('temperature') || t.contains('temp')) result.add('Measure temperature.');
    if (result.isEmpty) result.add('Translate the natural-language request into a testable embedded-system behavior.');
    return result;
  }

  List<String> _components(String text) {
    final t = text.toLowerCase();
    final result = <String>[];
    void add(String value) { if (!result.contains(value)) result.add(value); }
    if (t.contains('arduino')) add('Arduino-compatible MCU');
    if (t.contains('esp32')) add('ESP32 MCU');
    if (t.contains('esp8266')) add('ESP8266 MCU');
    if (t.contains('raspberry pi')) add('Raspberry Pi');
    if (t.contains('motor')) add('DC motor(s)');
    if (t.contains('servo')) add('Servo motor(s)');
    if (t.contains('stepper')) add('Stepper motor + driver');
    if (t.contains('motor driver') || t.contains('l298') || t.contains('l293')) add('Motor driver');
    if (t.contains('ir') || t.contains('infrared') || t.contains('line')) add('IR reflectance sensor array');
    if (t.contains('ultrasonic') || t.contains('distance')) add('Ultrasonic distance sensor');
    if (t.contains('temperature') || t.contains('temp')) add('Temperature sensor');
    if (t.contains('led')) add('LED indicator');
    if (t.contains('button') || t.contains('switch')) add('Push button / switch');
    if (t.contains('bluetooth')) add('Bluetooth module / radio');
    if (t.contains('wifi')) add('Wi-Fi radio');
    if (t.contains('battery') || t.contains('lipo')) add('Battery pack');
    if (t.contains('relay')) add('Relay module');
    if (result.isEmpty) add('MCU / controller');
    return result;
  }

  List<String> _architecture(String text, List<String> components) {
    final t = text.toLowerCase();
    return [
      'Controller layer: ${components.first}.',
      'Sensing layer: acquire and normalize sensor readings.',
      if (t.contains('motor') || t.contains('servo') || t.contains('stepper')) 'Actuation layer: command actuators through appropriate drivers.',
      if (t.contains('bluetooth') || t.contains('wifi')) 'Communication layer: isolate wireless I/O from control logic.',
      'Control layer: deterministic state machine / control loop.',
      'Verification layer: validate requirements, connections, power assumptions and generated firmware.',
    ];
  }

  List<String> _connections(String text, List<String> components) {
    final t = text.toLowerCase();
    final result = <String>[];
    if (components.any((c) => c.contains('IR'))) result.add('IR sensors → MCU digital/analog inputs');
    if (components.any((c) => c.contains('Ultrasonic'))) result.add('Ultrasonic TRIG/ECHO → MCU GPIO');
    if (components.any((c) => c.contains('Temperature'))) result.add('Temperature sensor → MCU sensor input/bus');
    if (components.any((c) => c.contains('motor'))) result.add('MCU control pins → motor driver → motors');
    if (components.any((c) => c.contains('Servo'))) result.add('MCU PWM-capable pin → servo signal');
    if (components.any((c) => c.contains('LED'))) result.add('MCU GPIO → LED through current-limiting resistor');
    if (t.contains('battery') || t.contains('lipo')) result.add('Battery → protected power path → regulated rails as required');
    return result;
  }

  List<String> _warnings(String text, List<String> components) {
    final t = text.toLowerCase();
    final result = <String>[];
    if (components.any((c) => c.contains('motor'))) result.add('Motor current and driver rating must be checked against the selected motors and supply.');
    if (t.contains('lipo')) result.add('LiPo battery systems require an appropriate protection/charging setup and correct voltage regulation.');
    if (components.any((c) => c.contains('Relay'))) result.add('Inductive loads need appropriate suppression and isolation practices.');
    result.add('Pin assignments, voltage levels and current limits must be confirmed against the exact hardware revision.');
    return result;
  }

  String _firmware(String text, List<String> components) {
    final t = text.toLowerCase();
    final isLine = t.contains('line') && (t.contains('follow') || t.contains('follower'));
    final hasMotor = components.any((c) => c.contains('motor'));
    final sensorSetup = isLine ? 'const int LEFT_SENSOR = 2;\nconst int RIGHT_SENSOR = 3;' : 'const int STATUS_LED = 13;';
    final loopBody = isLine && hasMotor
        ? '''\n  const bool left = digitalRead(LEFT_SENSOR);\n  const bool right = digitalRead(RIGHT_SENSOR);\n\n  // Replace these decisions with calibrated sensor thresholds for the exact robot.\n  if (left && right) { stopMotors(); }\n  else if (left) { turnLeft(); }\n  else if (right) { turnRight(); }\n  else { driveForward(); }\n'''
        : '''\n  // TODO: map the validated hardware specification to concrete pins.\n  // Keep control logic deterministic and non-blocking where possible.\n''';
    return '''// RoboLab generated firmware scaffold\n// Generated from a structured engineering plan. Verify pinout and electrical limits before flashing.\n\n$sensorSetup\n\nvoid setup() {\n  Serial.begin(115200);\n  pinMode(STATUS_LED, OUTPUT);\n  ${isLine ? 'pinMode(LEFT_SENSOR, INPUT);\n  pinMode(RIGHT_SENSOR, INPUT);' : ''}\n}\n\nvoid loop() {$loopBody\n}\n\nvoid driveForward() {}\nvoid turnLeft() {}\nvoid turnRight() {}\nvoid stopMotors() {}\n''';
  }

  List<ValidationResult> _verify(String prompt, List<String> components, List<String> connections, String code, List<String> warnings) {
    return [
      ValidationResult(ok: prompt.length >= 12, title: 'Requirement completeness', details: prompt.length >= 12 ? 'Request is long enough for an initial engineering pass.' : 'Add controller, inputs, outputs and desired behavior.'),
      ValidationResult(ok: components.isNotEmpty, title: 'Component coverage', details: '${components.length} candidate component(s) identified.'),
      ValidationResult(ok: connections.isNotEmpty, title: 'Connection plan', details: connections.isNotEmpty ? '${connections.length} connection rule(s) proposed.' : 'No connection can be safely inferred yet.'),
      ValidationResult(ok: code.trim().isNotEmpty, title: 'Code generation', details: 'Firmware scaffold generated with explicit hardware-review points.'),
      ValidationResult(ok: warnings.isNotEmpty, title: 'Engineering review gate', details: 'Review warnings and verify exact component datasheets before hardware use.'),
    ];
  }
}
