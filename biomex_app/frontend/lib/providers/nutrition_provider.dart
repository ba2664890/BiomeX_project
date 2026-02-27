import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import '../services/nutrition_service.dart';

class NutritionProvider extends ChangeNotifier {
  final NutritionService _nutritionService = NutritionService();
  
  bool _isLoading = false;
  String? _error;
  List<dynamic> _superfoods = [];
  List<dynamic> _foodsToAvoid = [];
  List<dynamic> _recipes = [];
  List<dynamic> _recommendedRecipes = [];
  List<dynamic> _foodSubstitutions = [];
  List<dynamic> _seasonalFoods = [];
  Map<String, dynamic>? _nutritionDashboard;

  bool get isLoading => _isLoading;
  String? get error => _error;
  List<dynamic> get superfoods => _superfoods;
  List<dynamic> get foodsToAvoid => _foodsToAvoid;
  List<dynamic> get recipes => _recipes;
  List<dynamic> get recommendedRecipes => _recommendedRecipes;
  List<dynamic> get foodSubstitutions => _foodSubstitutions;
  List<dynamic> get seasonalFoods => _seasonalFoods;
  Map<String, dynamic>? get nutritionDashboard => _nutritionDashboard;

  bool _notifyPending = false;
  void _safeNotify() {
    if (_notifyPending) return;
    _notifyPending = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _notifyPending = false;
      notifyListeners();
    });
  }

  Future<void> loadSuperfoods() async {
    _isLoading = true;
    _error = null;
    try {
      _superfoods = await _nutritionService.getSuperfoods();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadFoodsToAvoid() async {
    _isLoading = true;
    _error = null;
    try {
      _foodsToAvoid = await _nutritionService.getFoodsToAvoid();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadRecipes({String? tag, String? difficulty}) async {
    _isLoading = true;
    _error = null;
    try {
      _recipes = await _nutritionService.getRecipes(tag: tag, difficulty: difficulty);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadRecommendedRecipes() async {
    _isLoading = true;
    _error = null;
    try {
      _recommendedRecipes = await _nutritionService.getRecommendedRecipes();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadFoodSubstitutions() async {
    _isLoading = true;
    _error = null;
    try {
      _foodSubstitutions = await _nutritionService.getFoodSubstitutions();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadSeasonalFoods({String region = 'Dakar', int? month}) async {
    _isLoading = true;
    _error = null;
    try {
      _seasonalFoods = await _nutritionService.getSeasonalCalendar(region: region, month: month);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadNutritionDashboard() async {
    _isLoading = true;
    _error = null;
    try {
      _nutritionDashboard = await _nutritionService.getNutritionDashboard();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<Map<String, dynamic>?> initializeNutritionData() async {
    _isLoading = true;
    _error = null;
    try {
      final result = await _nutritionService.initializeNutritionData();
      await loadNutritionDashboard();
      _error = null;
      return result;
    } catch (e) {
      _error = e.toString();
      return null;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadAllData() async {
    _isLoading = true;
    _error = null;
    try {
      await Future.wait([
        loadSuperfoods(),
        loadFoodsToAvoid(),
        loadRecommendedRecipes(),
        loadFoodSubstitutions(),
        loadSeasonalFoods(),
        loadNutritionDashboard(),
      ]);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  void clearError() {
    _error = null;
    _safeNotify();
  }
}
