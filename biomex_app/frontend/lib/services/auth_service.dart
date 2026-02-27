import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../constants/api_constants.dart';
import 'api_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  ApiService get _apiService => ApiService();

  // Keys for secure storage
  static const String _tokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userKey = 'user_data';

  // Save token
  Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  // Get token
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  // Save refresh token
  Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _refreshTokenKey, value: token);
  }

  // Get refresh token
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  // Save user data
  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await _storage.write(key: _userKey, value: jsonEncode(userData));
  }

  // Get user data
  Future<Map<String, dynamic>?> getUserData() async {
    final userData = await _storage.read(key: _userKey);
    if (userData != null) {
      return jsonDecode(userData);
    }
    return null;
  }

  // Clear all data (logout)
  Future<void> logout() async {
    await _storage.deleteAll();
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    if (token == null) return false;

    // Check if token is expired
    try {
      bool isExpired = JwtDecoder.isExpired(token);
      return !isExpired;
    } catch (e) {
      return false;
    }
  }

  // Login
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _apiService.post(
      ApiConstants.login,
      body: {
        'email': email,
        'password': password,
      },
    );

    if (response != null) {
      await saveToken(response['access']);
      await saveRefreshToken(response['refresh']);
      
      // Get user data
      final userData = await getProfile();
      await saveUserData(userData);
      
      return response;
    }
    
    throw Exception('Erreur de connexion');
  }

  // Register
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String passwordConfirm,
    required String firstName,
    required String lastName,
    String? phone,
  }) async {
    final response = await _apiService.post(
      ApiConstants.register,
      body: {
        'email': email,
        'password': password,
        'password_confirm': passwordConfirm,
        'first_name': firstName,
        'last_name': lastName,
        'username': email,
        if (phone != null) 'phone': phone,
      },
    );

    return response;
  }

  // Get profile
  Future<Map<String, dynamic>> getProfile() async {
    final response = await _apiService.get(ApiConstants.profile);
    return response;
  }

  // Update profile
  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final response = await _apiService.put(ApiConstants.profile, body: data);
    
    // Update stored user data
    if (response != null) {
      await saveUserData(response);
    }
    
    return response;
  }

  // Change password
  Future<Map<String, dynamic>> changePassword({
    required String oldPassword,
    required String newPassword,
    required String newPasswordConfirm,
  }) async {
    final response = await _apiService.post(
      ApiConstants.changePassword,
      body: {
        'old_password': oldPassword,
        'new_password': newPassword,
        'new_password_confirm': newPasswordConfirm,
      },
    );

    return response;
  }

  // Get user dashboard
  Future<Map<String, dynamic>> getDashboard() async {
    final response = await _apiService.get(ApiConstants.dashboard);
    return response;
  }

  // Get user ID from token
  Future<int?> getUserId() async {
    final token = await getToken();
    if (token == null) return null;

    try {
      final decodedToken = JwtDecoder.decode(token);
      return decodedToken['user_id'];
    } catch (e) {
      return null;
    }
  }
}
