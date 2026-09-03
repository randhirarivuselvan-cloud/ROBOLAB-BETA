import '../models/generation_result.dart';
import '../services/api_service.dart';
import 'robolab_engine.dart';

class RoboLabAiOrchestrator {
  const RoboLabAiOrchestrator({
    required this.api,
    this.engine = const RoboLabEngine(),
  });

  final RoboLabApiService api;
  final RoboLabEngine engine;

  Future<GenerationResult> generate(String prompt) async {
    final trimmed = prompt.trim();
    if (trimmed.length < 12) {
      throw ArgumentError('Describe the project in a little more detail.');
    }

    try {
      final remote = await api.generateProject(trimmed);
      return GenerationResult.fromJson(remote);
    } catch (_) {
      final project = engine.run(trimmed);
      return GenerationResult(
        summary: 'RoboLab generated a structured engineering plan using the local analysis engine.',
        architecture: project.architecture,
        components: project.components,
        connections: project.connections,
        firmware: project.generatedCode,
        validation: project.verification
            .map((v) => GenerationCheck(ok: v.ok, name: v.title, details: v.details))
            .toList(),
        source: 'local-engine',
      );
    }
  }
}
