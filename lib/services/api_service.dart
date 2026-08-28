import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/profile.dart';

class ApiService {
  // FIX: URL configurable desde SettingsScreen
  // Emulador Android: 10.0.2.2 | Dispositivo físico: IP del PC en la red local
  static String _baseUrl = 'http://10.0.2.2:8000';

  static String get baseUrl => _baseUrl;

  static void setBaseUrl(String url) {
    // Normalizar: quitar slash final
    _baseUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
  }

  // FIX: timeout de 75 segundos (mayor que time_limit_sec=60 del solver)
  static const Duration _timeout = Duration(seconds: 75);

  static Future<DietResult> calculateDiet(Map<String, dynamic> payload) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl/optimize'),
            headers: {'Content-Type': 'application/json; charset=utf-8'},
            body: jsonEncode(payload),
          )
          .timeout(
            _timeout,
            onTimeout: () => throw Exception(
              'Tiempo de espera agotado (${_timeout.inSeconds}s). '
              'Verifica que el servidor esté corriendo en $_baseUrl',
            ),
          );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return DietResult.fromJson(data as Map<String, dynamic>);
      } else {
        String detail;
        try {
          final err = jsonDecode(response.body);
          detail = err['detail']?.toString() ?? response.body;
        } catch (_) {
          detail = response.body;
        }
        throw Exception('Error ${response.statusCode}: $detail');
      }
    } on Exception {
      rethrow;
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  /// Verifica si la API está disponible
  static Future<bool> checkHealth() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
