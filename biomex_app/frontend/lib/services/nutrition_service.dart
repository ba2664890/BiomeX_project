import '../constants/api_constants.dart';
import 'api_service.dart';

class NutritionService {
  static final NutritionService _instance = NutritionService._internal();
  factory NutritionService() => _instance;
  NutritionService._internal();

  final ApiService _apiService = ApiService();

  // Search foods
  Future<List<dynamic>> searchFoods(String query, {String? category}) async {
    String endpoint = '${ApiConstants.foodSearch}?q=$query';
    if (category != null) {
      endpoint += '&category=$category';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Get superfoods
  Future<List<dynamic>> getSuperfoods() async {
    final response = await _apiService.get(ApiConstants.superfoods);
    return response is List ? response : [];
  }

  // Get foods to avoid
  Future<List<dynamic>> getFoodsToAvoid() async {
    final response = await _apiService.get(ApiConstants.foodsToAvoid);
    return response is List ? response : [];
  }

  // Get recipes
  Future<List<dynamic>> getRecipes({String? tag, String? difficulty}) async {
    String endpoint = ApiConstants.recipes;
    if (tag != null) {
      endpoint += '?tag=$tag';
    }
    if (difficulty != null) {
      endpoint += '${tag != null ? '&' : '?'}difficulty=$difficulty';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Get recipe detail
  Future<Map<String, dynamic>> getRecipeDetail(int id) async {
    return await _apiService.get('${ApiConstants.recipes}$id/');
  }

  // Get recommended recipes
  Future<List<dynamic>> getRecommendedRecipes() async {
    final response = await _apiService.get(ApiConstants.recommendedRecipes);
    return response is List ? response : [];
  }

  // Get food substitutions
  Future<List<dynamic>> getFoodSubstitutions() async {
    final response = await _apiService.get(ApiConstants.foodSubstitutions);
    return response is List ? response : [];
  }

  // Get seasonal calendar
  Future<List<dynamic>> getSeasonalCalendar({String region = 'Dakar', int? month}) async {
    String endpoint = '${ApiConstants.seasonalCalendar}?region=$region';
    if (month != null) {
      endpoint += '&month=$month';
    }
    final response = await _apiService.get(endpoint);
    return response is List ? response : [];
  }

  // Get nutrition dashboard
  Future<Map<String, dynamic>> getNutritionDashboard() async {
    return await _apiService.get(ApiConstants.nutritionDashboard);
  }

  // Initialize nutrition data (for demo)
  Future<Map<String, dynamic>> initializeNutritionData() async {
    return await _apiService.post(ApiConstants.initializeNutritionData);
  }
}
