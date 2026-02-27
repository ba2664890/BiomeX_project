import '../constants/api_constants.dart';
import 'api_service.dart';

class TrackingService {
  static final TrackingService _instance = TrackingService._internal();
  factory TrackingService() => _instance;
  TrackingService._internal();

  final ApiService _apiService = ApiService();

  // Get tracking dashboard
  Future<Map<String, dynamic>> getTrackingDashboard() async {
    return await _apiService.get(ApiConstants.trackingDashboard);
  }

  // Get wellness checks
  Future<List<dynamic>> getWellnessChecks() async {
    final response = await _apiService.get(ApiConstants.wellnessChecks);
    return response is List ? response : [];
  }

  // Create wellness check
  Future<Map<String, dynamic>> createWellnessCheck({
    required String date,
    required String category,
    required int rating,
    String? notes,
  }) async {
    return await _apiService.post(
      ApiConstants.createWellnessCheck,
      body: {
        'date': date,
        'category': category,
        'rating': rating,
        if (notes != null) 'notes': notes,
      },
    );
  }

  // Get health metrics
  Future<List<dynamic>> getHealthMetrics({String? type}) async {
    String endpoint = ApiConstants.healthMetrics;
    if (type != null) {
      endpoint += '?type=$type';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Create health metric
  Future<Map<String, dynamic>> createHealthMetric({
    required String metricType,
    required double value,
    required String date,
    String? notes,
  }) async {
    return await _apiService.post(
      ApiConstants.createHealthMetric,
      body: {
        'metric_type': metricType,
        'value': value,
        'date': date,
        if (notes != null) 'notes': notes,
      },
    );
  }

  // Get symptom logs
  Future<List<dynamic>> getSymptomLogs() async {
    final response = await _apiService.get(ApiConstants.symptomLogs);
    return response is List ? response : [];
  }

  // Create symptom log
  Future<Map<String, dynamic>> createSymptomLog({
    required String symptom,
    required String severity,
    required String date,
    int? durationHours,
    String? notes,
  }) async {
    return await _apiService.post(
      ApiConstants.createSymptomLog,
      body: {
        'symptom': symptom,
        'severity': severity,
        'date': date,
        if (durationHours != null) 'duration_hours': durationHours,
        if (notes != null) 'notes': notes,
      },
    );
  }

  // Get weekly insights
  Future<List<dynamic>> getWeeklyInsights() async {
    final response = await _apiService.get(ApiConstants.weeklyInsights);
    return response is List ? response : [];
  }

  // Mark insight as read
  Future<Map<String, dynamic>> markInsightRead(int id) async {
    return await _apiService.post('${ApiConstants.weeklyInsights}$id/read/');
  }

  // Get routines
  Future<List<dynamic>> getRoutines() async {
    final response = await _apiService.get(ApiConstants.routines);
    return response is List ? response : [];
  }

  // Create routine
  Future<Map<String, dynamic>> createRoutine({
    required String name,
    required String routineType,
    String? description,
    String? timeOfDay,
  }) async {
    return await _apiService.post(
      ApiConstants.createRoutine,
      body: {
        'name': name,
        'routine_type': routineType,
        if (description != null) 'description': description,
        if (timeOfDay != null) 'time_of_day': timeOfDay,
      },
    );
  }

  // Log routine
  Future<Map<String, dynamic>> logRoutine({
    required int routineId,
    required String date,
    required bool completed,
    String? notes,
  }) async {
    return await _apiService.post(
      ApiConstants.routineLog,
      body: {
        'routine': routineId,
        'date': date,
        'completed': completed,
        if (notes != null) 'notes': notes,
      },
    );
  }

  // Initialize tracking data (for demo)
  Future<Map<String, dynamic>> initializeTrackingData() async {
    return await _apiService.post(ApiConstants.initializeTrackingData);
  }
}
