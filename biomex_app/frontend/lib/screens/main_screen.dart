import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/app_theme.dart';
import '../providers/microbiome_provider.dart';
import '../providers/nutrition_provider.dart';
import '../providers/tracking_provider.dart';
import 'home/home_screen.dart';
import 'report/report_screen.dart';
import 'nutrition/nutrition_screen.dart';
import 'tracking/tracking_screen.dart';
import 'profile/profile_screen.dart';
import 'chat/chat_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    ReportScreen(),
    NutritionScreen(),
    TrackingScreen(),
    ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialData();
    });
  }

  Future<void> _loadInitialData() async {
    final microbiomeProvider =
        Provider.of<MicrobiomeProvider>(context, listen: false);
    final nutritionProvider =
        Provider.of<NutritionProvider>(context, listen: false);
    final trackingProvider =
        Provider.of<TrackingProvider>(context, listen: false);

    // Load all data in parallel
    await Future.wait([
      microbiomeProvider.loadDashboardScores(),
      nutritionProvider.loadNutritionDashboard(),
      trackingProvider.loadTrackingDashboard(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final fabBottomPadding = MediaQuery.of(context).padding.bottom + 28;

    return Scaffold(
      extendBody: true,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      floatingActionButton: Padding(
        padding: EdgeInsets.only(bottom: fabBottomPadding),
        child: FloatingActionButton.extended(
          heroTag: 'chat_fab',
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ChatScreen()),
            );
          },
          backgroundColor: AppColors.accent,
          foregroundColor: AppColors.primaryDark,
          icon: const Icon(Icons.chat_bubble_outline_rounded),
          label: const Text(
            'Chat',
            style: TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(left: 20, right: 20, bottom: 20),
          child: Container(
            height: 70,
            decoration: BoxDecoration(
              color: AppColors.primaryDark,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.2),
                  blurRadius: 15,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(0, Icons.home_outlined, Icons.home, 'Accueil'),
                _buildNavItem(
                    1, Icons.assessment_outlined, Icons.assessment, 'Rapport'),
                _buildNavItem(2, Icons.restaurant_outlined, Icons.restaurant,
                    'Nutrition'),
                _buildNavItem(
                    3, Icons.trending_up_outlined, Icons.trending_up, 'Suivi'),
                _buildNavItem(4, Icons.person_outline, Icons.person, 'Profil'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(
      int index, IconData icon, IconData activeIcon, String label) {
    final isSelected = _currentIndex == index;

    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      behavior: HitTestBehavior.opaque,
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          // Background layout for spacing
          SizedBox(
            width: 70,
            height: 70,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 24), // Space placeholder for icon
                if (!isSelected) ...[
                  const SizedBox(height: 4),
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w500,
                      color: Colors.white54,
                    ),
                  ),
                ]
              ],
            ),
          ),

          // Animated pop-out icon
          AnimatedPositioned(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOutBack,
            top: isSelected ? -20 : 18,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: isSelected ? 50 : 28,
                  height: isSelected ? 50 : 28,
                  decoration: BoxDecoration(
                    color:
                        isSelected ? AppColors.primaryDark : Colors.transparent,
                    shape: BoxShape.circle,
                    border: isSelected
                        ? Border.all(color: AppColors.accent, width: 2)
                        : null,
                  ),
                  child: Icon(
                    isSelected ? activeIcon : icon,
                    color: isSelected ? AppColors.accent : Colors.white54,
                    size: isSelected ? 24 : 26,
                  ),
                ),
                if (isSelected) ...[
                  const SizedBox(height: 8),
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppColors.accent,
                    ),
                  ),
                ]
              ],
            ),
          ),
        ],
      ),
    );
  }
}
