import '../models/project.dart';

class EngineeringPipeline {
  const EngineeringPipeline();

  RoboProject analyze(RoboProject project) {
    final text = project.prompt.toLowerCase();
    final components = <String>[];
    if (text.contains('arduino')) components.add('Arduino-compatible MCU');
    if (text.contains('motor') || text.contains('robot')) components.add('Motor driver');
    if (text.contains('ir') || text.contains('line')) components.add('IR sensor array');
    if (text.contains('servo')) components.add('Servo motor');
    if (text.contains('ultrasonic') || text.contains('distance')) components.add('Ultrasonic distance sensor');
    if (components.isEmpty) components.add('MCU / controller');
    return project.copyWith(stage: ProjectStage.planning, components: components);
  }

  List<ValidationResult> validate(RoboProject project) {
    final results = <ValidationResult>[];
    results.add(ValidationResult(ok: project.components.isNotEmpty, title: 'Component coverage', details: '${project.components.length} candidate component(s) identified.'));
    results.add(ValidationResult(ok: project.prompt.trim().length >= 12, title: 'Requirement quality', details: project.prompt.trim().length >= 12 ? 'Natural-language requirement is detailed enough for a first pass.' : 'Add more detail about behavior, controller and hardware.'));
    results.add(const ValidationResult(ok: true, title: 'Safety gate', details: 'No physical wiring has been executed by the app. Hardware output requires review before use.'));
    return results;
  }
}
