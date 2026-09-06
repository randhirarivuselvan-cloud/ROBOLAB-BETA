import '../services/api_service.dart';

class RoboLabAppConfig {
  const RoboLabAppConfig._();

  static const apiBaseUrl = String.fromEnvironment(
    'ROBOLAB_API_URL',
    defaultValue: '',
  );

  static RoboLabApiService? get api {
    final url = apiBaseUrl.trim();
    return url.isEmpty ? null : RoboLabApiService(baseUrl: url);
  }
}
