import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import 'auth_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  AuthService get _authService => AuthService();

  // GET request
  Future<dynamic> get(String endpoint) async {
    try {
      final token = await _authService.getToken();
      final headers = token != null
          ? ApiConstants.authorizedHeaders(token)
          : ApiConstants.headers;

      final response = await http.get(
        Uri.parse(endpoint),
        headers: headers,
      );

      return _handleResponse(response);
    } on SocketException {
      throw Exception('Pas de connexion internet');
    } catch (e) {
      throw Exception('Erreur: $e');
    }
  }

  // POST request
  Future<dynamic> post(String endpoint, {Map<String, dynamic>? body}) async {
    try {
      final token = await _authService.getToken();
      final headers = token != null
          ? ApiConstants.authorizedHeaders(token)
          : ApiConstants.headers;

      final response = await http.post(
        Uri.parse(endpoint),
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );

      return _handleResponse(response);
    } on SocketException {
      throw Exception('Pas de connexion internet');
    } catch (e) {
      throw Exception('Erreur: $e');
    }
  }

  // PUT request
  Future<dynamic> put(String endpoint, {Map<String, dynamic>? body}) async {
    try {
      final token = await _authService.getToken();
      final headers = token != null
          ? ApiConstants.authorizedHeaders(token)
          : ApiConstants.headers;

      final response = await http.put(
        Uri.parse(endpoint),
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );

      return _handleResponse(response);
    } on SocketException {
      throw Exception('Pas de connexion internet');
    } catch (e) {
      throw Exception('Erreur: $e');
    }
  }

  // PATCH request
  Future<dynamic> patch(String endpoint, {Map<String, dynamic>? body}) async {
    try {
      final token = await _authService.getToken();
      final headers = token != null
          ? ApiConstants.authorizedHeaders(token)
          : ApiConstants.headers;

      final response = await http.patch(
        Uri.parse(endpoint),
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );

      return _handleResponse(response);
    } on SocketException {
      throw Exception('Pas de connexion internet');
    } catch (e) {
      throw Exception('Erreur: $e');
    }
  }

  // DELETE request
  Future<dynamic> delete(String endpoint) async {
    try {
      final token = await _authService.getToken();
      final headers = token != null
          ? ApiConstants.authorizedHeaders(token)
          : ApiConstants.headers;

      final response = await http.delete(
        Uri.parse(endpoint),
        headers: headers,
      );

      return _handleResponse(response);
    } on SocketException {
      throw Exception('Pas de connexion internet');
    } catch (e) {
      throw Exception('Erreur: $e');
    }
  }

  // Handle response
  dynamic _handleResponse(http.Response response) {
    final statusCode = response.statusCode;
    final body = response.body.isNotEmpty ? jsonDecode(response.body) : null;

    if (statusCode >= 200 && statusCode < 300) {
      return body;
    } else if (statusCode == 401) {
      // Token expired or invalid
      _authService.logout();
      throw Exception('Session expirée. Veuillez vous reconnecter.');
    } else if (statusCode == 403) {
      throw Exception('Accès non autorisé');
    } else if (statusCode == 404) {
      throw Exception('Ressource non trouvée');
    } else if (statusCode >= 400 && statusCode < 500) {
      final errorMessage = body is Map
          ? body['detail'] ??
              body['message'] ??
              body['error'] ??
              'Erreur de requête'
          : 'Erreur de requête';
      throw Exception(errorMessage);
    } else if (statusCode >= 500) {
      final errorMessage = body is Map
          ? body['detail'] ??
              body['message'] ??
              body['error'] ??
              'Erreur serveur. Veuillez réessayer plus tard.'
          : 'Erreur serveur. Veuillez réessayer plus tard.';
      throw Exception(errorMessage);
    } else {
      throw Exception('Erreur inattendue.');
    }
  }

  // Check if token is valid
  Future<bool> isTokenValid() async {
    final token = await _authService.getToken();
    if (token == null) return false;

    try {
      final response =
          await post(ApiConstants.verifyToken, body: {'token': token});
      return response != null;
    } catch (e) {
      return false;
    }
  }

  // Refresh token
  Future<bool> refreshToken() async {
    final refreshToken = await _authService.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await post(ApiConstants.refreshToken,
          body: {'refresh': refreshToken});
      if (response != null && response['access'] != null) {
        await _authService.saveToken(response['access']);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
