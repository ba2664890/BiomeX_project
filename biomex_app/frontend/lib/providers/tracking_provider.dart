import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import '../services/tracking_service.dart';

class TrackingProvider extends ChangeNotifier {
  final TrackingService _trackingService = TrackingService();
  
  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _trackingDashboard;
  List<dynamic> _wellnessChecks = [];
  List<dynamic> _healthMetrics = [];
  List<dynamic> _symptomLogs = [];
  List<dynamic> _weeklyInsights = [];
  List<dynamic> _routines = [];

  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, dynamic>? get trackingDashboard => _trackingDashboard;
  List<dynamic> get wellnessChecks => _wellnessChecks;
  List<dynamic> get healthMetrics => _healthMetrics;
  List<dynamic> get symptomLogs => _symptomLogs;
  List<dynamic> get weeklyInsights => _weeklyInsights;
  List<dynamic> get routines => _routines;

  bool _notifyPending = false;
  void _safeNotify() {
    if (_notifyPending) return;
    _notifyPending = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _notifyPending = false;
      notifyListeners();
    });
  }

  Future<void> loadTrackingDashboard() async {
    _isLoading = true;
    _error = null;
    try {
      _trackingDashboard = await _trackingService.getTrackingDashboard();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadWellnessChecks() async {
    _isLoading = true;
    _error = null;
    try {
      _wellnessChecks = await _trackingService.getWellnessChecks();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> createWellnessCheck({
    required String date,
    required String category,
    required int rating,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.createWellnessCheck(date: date, category: category, rating: rating, notes: notes);
      await loadWellnessChecks();
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadHealthMetrics({String? type}) async {
    _isLoading = true;
    _error = null;
    try {
      _healthMetrics = await _trackingService.getHealthMetrics(type: type);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> createHealthMetric({
    required String metricType,
    required double value,
    required String date,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.createHealthMetric(metricType: metricType, value: value, date: date, notes: notes);
      await loadHealthMetrics();
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadSymptomLogs() async {
    _isLoading = true;
    _error = null;
    try {
      _symptomLogs = await _trackingService.getSymptomLogs();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> createSymptomLog({
    required String symptom,
    required String severity,
    required String date,
    int? durationHours,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.createSymptomLog(symptom: symptom, severity: severity, date: date, durationHours: durationHours, notes: notes);
      await loadSymptomLogs();
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadWeeklyInsights() async {
    _isLoading = true;
    _error = null;
    try {
      _weeklyInsights = await _trackingService.getWeeklyInsights();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> markInsightRead(int id) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.markInsightRead(id);
      await loadWeeklyInsights();
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<void> loadRoutines() async {
    _isLoading = true;
    _error = null;
    try {
      _routines = await _trackingService.getRoutines();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> createRoutine({
    required String name,
    required String routineType,
    String? description,
    String? timeOfDay,
  }) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.createRoutine(name: name, routineType: routineType, description: description, timeOfDay: timeOfDay);
      await loadRoutines();
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<bool> logRoutine({
    required int routineId,
    required String date,
    required bool completed,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    try {
      await _trackingService.logRoutine(routineId: routineId, date: date, completed: completed, notes: notes);
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      _safeNotify();
    }
  }

  Future<Map<String, dynamic>?> initializeTrackingData() async {
    _isLoading = true;
    _error = null;
    try {
      final result = await _trackingService.initializeTrackingData();
      await loadTrackingDashboard();
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
        loadTrackingDashboard(),
        loadWellnessChecks(),
        loadWeeklyInsights(),
        loadRoutines(),
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
