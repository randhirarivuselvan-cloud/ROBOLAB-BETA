enum ProjectStage { draft, planning, circuit, code, verification, ready, error }

class RoboProject {
  RoboProject({required this.id, required this.name, required this.prompt, this.stage = ProjectStage.draft, this.components = const [], this.connections = const [], this.generatedCode = ''});

  final String id;
  final String name;
  final String prompt;
  final ProjectStage stage;
  final List<String> components;
  final List<String> connections;
  final String generatedCode;

  RoboProject copyWith({ProjectStage? stage, List<String>? components, List<String>? connections, String? generatedCode}) => RoboProject(
        id: id, name: name, prompt: prompt, stage: stage ?? this.stage,
        components: components ?? this.components, connections: connections ?? this.connections,
        generatedCode: generatedCode ?? this.generatedCode,
      );
}

class ValidationResult {
  const ValidationResult({required this.ok, required this.title, required this.details});
  final bool ok;
  final String title;
  final String details;
}
