import 'dart:convert';
import 'package:http/http.dart' as http;

class RoboLabApiService {
  const RoboLabApiService({required this.baseUrl});
  final String baseUrl;

  Future<Map<String, dynamic>> generateProject(String prompt) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/projects/generate'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode({'prompt': prompt}),
    );
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('RoboLab API error ${response.statusCode}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getPlans() async {
    final response = await http.get(Uri.parse('$baseUrl/api/v1/plans'));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('RoboLab plans error ${response.statusCode}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<String> exportProject(Map<String, dynamic> result) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/projects/export'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode({'result': result}),
    );
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('RoboLab export error ${response.statusCode}');
    }
    return utf8.decode(response.bodyBytes);
  }
}
