import '../constants/api_constants.dart';
import 'api_service.dart';

class RecommendationService {
  static final RecommendationService _instance =
      RecommendationService._internal();
  factory RecommendationService() => _instance;
  RecommendationService._internal();

  final ApiService _apiService = ApiService();

  // Get user recommendations
  Future<List<dynamic>> getRecommendations() async {
    final response = await _apiService.get(ApiConstants.recommendations);
    return response is List ? response : [];
  }

  // Get recommendation detail
  Future<Map<String, dynamic>> getRecommendationDetail(int id) async {
    return await _apiService.get('${ApiConstants.recommendations}$id/');
  }

  // Mark recommendation as read
  Future<Map<String, dynamic>> markRecommendationRead(int id) async {
    return await _apiService.post('${ApiConstants.recommendations}$id/read/');
  }

  // Mark recommendation as completed
  Future<Map<String, dynamic>> markRecommendationCompleted(int id) async {
    return await _apiService
        .post('${ApiConstants.recommendations}$id/complete/');
  }

  // Get daily recommendations
  Future<List<dynamic>> getDailyRecommendations() async {
    final response = await _apiService.get(ApiConstants.dailyRecommendations);
    return response is List ? response : [];
  }

  // Get today's recommendations
  Future<Map<String, dynamic>> getTodaysRecommendations() async {
    return await _apiService.get(ApiConstants.todaysRecommendations);
  }

  // Create sample recommendations (for demo)
  Future<Map<String, dynamic>> createSampleRecommendations() async {
    return await _apiService.post(ApiConstants.createSampleRecommendations);
  }

  // Chatbot RAG
  Future<Map<String, dynamic>> askRagChatbot({
    required String question,
    int topK = 6,
    String? namespace,
  }) async {
    final payload = <String, dynamic>{
      'question': question,
      'top_k': topK,
    };
    if (namespace != null && namespace.trim().isNotEmpty) {
      payload['namespace'] = namespace.trim();
    }
    return await _apiService.post(ApiConstants.ragChat, body: payload);
  }
}
