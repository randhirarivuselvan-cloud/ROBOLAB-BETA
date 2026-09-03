class GenerationResult {
  const GenerationResult({
    required this.summary,
    required this.architecture,
    required this.components,
    required this.connections,
    required this.firmware,
    required this.validation,
    required this.source,
  });

  final String summary;
  final List<String> architecture;
  final List<String> components;
  final List<String> connections;
  final String firmware;
  final List<GenerationCheck> validation;
  final String source;

  bool get passed => validation.every((check) => check.ok);

  factory GenerationResult.fromJson(Map<String, dynamic> json) {
    List<String> strings(String key) =>
        (json[key] as List<dynamic>? ?? const []).map((e) => e.toString()).toList();

    return GenerationResult(
      summary: json['summary']?.toString() ?? '',
      architecture: strings('architecture'),
      components: strings('components'),
      connections: strings('connections'),
      firmware: json['firmware']?.toString() ?? '',
      validation: (json['validation'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(GenerationCheck.fromJson)
          .toList(),
      source: json['source']?.toString() ?? 'unknown',
    );
  }
}

class GenerationCheck {
  const GenerationCheck({required this.ok, required this.name, required this.details});

  final bool ok;
  final String name;
  final String details;

  factory GenerationCheck.fromJson(Map<String, dynamic> json) => GenerationCheck(
        ok: json['ok'] == true,
        name: json['name']?.toString() ?? 'Check',
        details: json['details']?.toString() ?? '',
      );
}
