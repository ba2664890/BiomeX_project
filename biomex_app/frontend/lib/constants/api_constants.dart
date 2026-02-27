class ApiConstants {
  // Base URL - Change this to your Django backend URL
  static const String baseUrl = 'https://biomex-project.onrender.com';
  // static const String baseUrl = 'http://10.0.2.2:8000'; // For Android emulator
  // static const String baseUrl = 'http://localhost:8000'; // For iOS simulator

  static const String apiUrl = '$baseUrl/api';

  // Auth Endpoints
  static const String login = '$apiUrl/token/';
  static const String refreshToken = '$apiUrl/token/refresh/';
  static const String verifyToken = '$apiUrl/token/verify/';
  static const String register = '$apiUrl/users/register/';
  static const String profile = '$apiUrl/users/profile/';
  static const String changePassword = '$apiUrl/users/change-password/';
  static const String dashboard = '$apiUrl/users/dashboard/';
  static const String notifications = '$apiUrl/users/notifications/';

  // Microbiome Endpoints
  static const String latestAnalysis = '$apiUrl/microbiome/latest/';
  static const String analysisList = '$apiUrl/microbiome/list/';
  static const String analysisDetail = '$apiUrl/microbiome/detail/';
  static const String dashboardScores = '$apiUrl/microbiome/dashboard-scores/';
  static const String bacteriaBalance = '$apiUrl/microbiome/bacteria-balance/';
  static const String healthMarkers = '$apiUrl/microbiome/health-markers/';
  static const String scoreHistory = '$apiUrl/microbiome/score-history/';
  static const String requestKit = '$apiUrl/microbiome/request-kit/';
  static const String createSampleAnalysis =
      '$apiUrl/microbiome/create-sample/';

  // Nutrition Endpoints
  static const String foodSearch = '$apiUrl/nutrition/search/';
  static const String superfoods = '$apiUrl/nutrition/superfoods/';
  static const String foodsToAvoid = '$apiUrl/nutrition/foods-to-avoid/';
  static const String recipes = '$apiUrl/nutrition/recipes/';
  static const String recommendedRecipes =
      '$apiUrl/nutrition/recipes/recommended/';
  static const String foodSubstitutions = '$apiUrl/nutrition/substitutions/';
  static const String seasonalCalendar = '$apiUrl/nutrition/seasonal/';
  static const String nutritionDashboard = '$apiUrl/nutrition/dashboard/';
  static const String initializeNutritionData =
      '$apiUrl/nutrition/initialize-data/';

  // Tracking Endpoints
  static const String trackingDashboard = '$apiUrl/tracking/dashboard/';
  static const String wellnessChecks = '$apiUrl/tracking/wellness/';
  static const String createWellnessCheck = '$apiUrl/tracking/wellness/create/';
  static const String healthMetrics = '$apiUrl/tracking/health-metrics/';
  static const String createHealthMetric =
      '$apiUrl/tracking/health-metrics/create/';
  static const String symptomLogs = '$apiUrl/tracking/symptoms/';
  static const String createSymptomLog = '$apiUrl/tracking/symptoms/create/';
  static const String weeklyInsights = '$apiUrl/tracking/insights/';
  static const String routines = '$apiUrl/tracking/routines/';
  static const String createRoutine = '$apiUrl/tracking/routines/create/';
  static const String routineLog = '$apiUrl/tracking/routines/log/';
  static const String initializeTrackingData =
      '$apiUrl/tracking/initialize-data/';

  // Recommendations Endpoints
  static const String recommendations = '$apiUrl/recommendations/';
  static const String dailyRecommendations = '$apiUrl/recommendations/daily/';
  static const String todaysRecommendations = '$apiUrl/recommendations/today/';
  static const String createSampleRecommendations =
      '$apiUrl/recommendations/create-sample/';
  static const String ragChat = '$apiUrl/recommendations/rag/chat/';
  static const String ragStatus = '$apiUrl/recommendations/rag/status/';

  // Headers
  static Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  static Map<String, String> authorizedHeaders(String token) {
    return {
      ...headers,
      'Authorization': 'Bearer $token',
    };
  }
}
