import '../models/generation_result.dart';
import '../services/api_service.dart';
import 'engineering_pipeline.dart';

class RoboLabAiOrchestrator {
  const RoboLabAiOrchestrator({
    required this.api,
    this.pipeline = const EngineeringPipeline(),
  });

  final RoboLabApiService api;
  final EngineeringPipeline pipeline;

  Future<GenerationResult> generate(String prompt) async {
    final trimmed = prompt.trim();
    if (trimmed.length < 12) {
      throw ArgumentError('Describe the project in a little more detail.');
    }

    try {
      final remote = await api.generateProject(trimmed);
      return GenerationResult.fromJson(remote);
    } catch (_) {
      return _localFallback(trimmed);
    }
  }

  GenerationResult _localFallback(String prompt) {
    final text = prompt.toLowerCase();
    final components = <String>[];
    final architecture = <String>[
      'Input/sensing layer',
      'Controller and decision layer',
      'Actuation/output layer',
      'Power and protection layer',
    ];
    final connections = <String>[];

    if (text.contains('arduino')) components.add('Arduino-compatible microcontroller');
    if (text.contains('esp32')) components.add('ESP32 development board');
    if (text.contains('motor')) components.add('Motor driver matched to motor current');
    if (text.contains('servo')) components.add('Servo motor');
    if (text.contains('ultrasonic') || text.contains('distance')) {
      components.add('Ultrasonic distance sensor');
    }
    if (text.contains('ir') || text.contains('line follow')) {
      components.add('IR reflectance sensor array');
    }
    if (components.isEmpty) components.add('Microcontroller appropriate for project I/O');

    if (components.any((c) => c.toLowerCase().contains('sensor'))) {
      connections.add('Sensors → controller input pins, using the sensor module voltage requirements');
    }
    if (components.any((c) => c.toLowerCase().contains('motor driver'))) {
      connections.add('Controller logic pins → motor driver inputs');
      connections.add('Motor supply → motor driver power input; grounds common only where electrically appropriate');
    }
    connections.add('Power source → regulated controller supply with protection and correct voltage/current rating');

    const firmware = '''// RoboLab local fallback skeleton
// A provider-backed backend should replace this with board-specific firmware.

void setup() {
  // Configure project-specific I/O here.
}

void loop() {
  // 1. Read sensors
  // 2. Apply control logic
  // 3. Update outputs
  // 4. Enforce timing and fail-safe behavior
}
''';

    final risky = text.contains('mains') ||
        text.contains('high voltage') ||
        text.contains('weapon') ||
        text.contains('explosive');

    return GenerationResult(
      summary: 'Local engineering analysis generated because the remote AI backend was unavailable.',
      architecture: architecture,
      components: components,
      connections: connections,
      firmware: firmware,
      validation: [
        GenerationCheck(
          ok: !risky,
          name: 'Safety gate',
          details: risky
              ? 'This request needs additional safety review before hardware guidance can be produced.'
              : 'No high-risk hardware category was detected by the local pre-check.',
        ),
        GenerationCheck(
          ok: components.isNotEmpty,
          name: 'Component coverage',
          details: '${components.length} candidate component(s) identified.',
        ),
        const GenerationCheck(
          ok: true,
          name: 'Backend status',
          details: 'Running deterministic local fallback; connect the RoboLab backend for model-generated code and circuit output.',
        ),
      ],
      source: 'local-fallback',
    );
  }
}
