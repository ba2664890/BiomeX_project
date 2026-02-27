import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import '../services/microbiome_service.dart';

class MicrobiomeProvider extends ChangeNotifier {
  final MicrobiomeService _microbiomeService = MicrobiomeService();
  
  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _dashboardScores;
  Map<String, dynamic>? _latestAnalysis;
  List<dynamic> _analysisList = [];
  List<dynamic> _bacteriaBalance = [];
  List<dynamic> _healthMarkers = [];
  List<dynamic> _scoreHistory = [];

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, dynamic>? get dashboardScores => _dashboardScores;
  Map<String, dynamic>? get latestAnalysis => _latestAnalysis;
  List<dynamic> get analysisList => _analysisList;
  List<dynamic> get bacteriaBalance => _bacteriaBalance;
  List<dynamic> get healthMarkers => _healthMarkers;
  List<dynamic> get scoreHistory => _scoreHistory;

  bool _notifyPending = false;
  void _safeNotify() {
    if (_notifyPending) return;
    _notifyPending = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _notifyPending = false;
      notifyListeners();
    });
  }

  // Load dashboard scores
  Future<void> loadDashboardScores() async {
    _isLoading = true;
    _error = null;

    try {
      _dashboardScores = await _microbiomeService.getDashboardScores();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Load latest analysis
  Future<void> loadLatestAnalysis() async {
    _isLoading = true;
    _error = null;

    try {
      _latestAnalysis = await _microbiomeService.getLatestAnalysis();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Load analysis list
  Future<void> loadAnalysisList() async {
    _isLoading = true;
    _error = null;

    try {
      _analysisList = await _microbiomeService.getAnalysisList();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Load bacteria balance
  Future<void> loadBacteriaBalance({int? analysisId}) async {
    _isLoading = true;
    _error = null;

    try {
      _bacteriaBalance = await _microbiomeService.getBacteriaBalance(analysisId: analysisId);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Load health markers
  Future<void> loadHealthMarkers({int? analysisId}) async {
    _isLoading = true;
    _error = null;

    try {
      _healthMarkers = await _microbiomeService.getHealthMarkers(analysisId: analysisId);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Load score history
  Future<void> loadScoreHistory() async {
    _isLoading = true;
    _error = null;

    try {
      _scoreHistory = await _microbiomeService.getScoreHistory();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Request new kit
  Future<Map<String, dynamic>?> requestNewKit() async {
    _isLoading = true;
    _error = null;

    try {
      final result = await _microbiomeService.requestNewKit();
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

  // Create sample analysis (for demo)
  Future<Map<String, dynamic>?> createSampleAnalysis() async {
    _isLoading = true;
    _error = null;

    try {
      final result = await _microbiomeService.createSampleAnalysis();
      await loadDashboardScores();
      await loadLatestAnalysis();
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

  // Load all data
  Future<void> loadAllData() async {
    _isLoading = true;
    _error = null;

    try {
      await Future.wait([
        loadDashboardScores(),
        loadLatestAnalysis(),
        loadBacteriaBalance(),
        loadHealthMarkers(),
        loadScoreHistory(),
      ]);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  // Clear error
  void clearError() {
    _error = null;
    _safeNotify();
  }
}
