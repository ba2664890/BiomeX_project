import '../constants/api_constants.dart';
import 'api_service.dart';

class MicrobiomeService {
  static final MicrobiomeService _instance = MicrobiomeService._internal();
  factory MicrobiomeService() => _instance;
  MicrobiomeService._internal();

  final ApiService _apiService = ApiService();

  // Get latest analysis
  Future<Map<String, dynamic>> getLatestAnalysis() async {
    return await _apiService.get(ApiConstants.latestAnalysis);
  }

  // Get analysis list
  Future<List<dynamic>> getAnalysisList() async {
    final response = await _apiService.get(ApiConstants.analysisList);
    return response is List ? response : [];
  }

  // Get analysis detail
  Future<Map<String, dynamic>> getAnalysisDetail(int id) async {
    return await _apiService.get('${ApiConstants.analysisDetail}$id/');
  }

  // Get dashboard scores
  Future<Map<String, dynamic>> getDashboardScores() async {
    return await _apiService.get(ApiConstants.dashboardScores);
  }

  // Get bacteria balance
  Future<List<dynamic>> getBacteriaBalance({int? analysisId}) async {
    String endpoint = ApiConstants.bacteriaBalance;
    if (analysisId != null) {
      endpoint = '${ApiConstants.bacteriaBalance}$analysisId/';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Get health markers
  Future<List<dynamic>> getHealthMarkers({int? analysisId}) async {
    String endpoint = ApiConstants.healthMarkers;
    if (analysisId != null) {
      endpoint = '${ApiConstants.healthMarkers}$analysisId/';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Get score history
  Future<List<dynamic>> getScoreHistory() async {
    final response = await _apiService.get(ApiConstants.scoreHistory);
    return response is List ? response : [];
  }

  // Request new kit
  Future<Map<String, dynamic>> requestNewKit() async {
    return await _apiService.post(ApiConstants.requestKit);
  }

  // Create sample analysis (for demo)
  Future<Map<String, dynamic>> createSampleAnalysis() async {
    return await _apiService.post(ApiConstants.createSampleAnalysis);
  }
}
