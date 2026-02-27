import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../constants/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/microbiome_provider.dart';
import '../../services/recommendation_service.dart';
import '../../widgets/animated_stage.dart';
import '../../widgets/hero_banner_card.dart';
import '../../widgets/media_reel_section.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> _recommendations = [];
  bool _isLoadingRec = true;
  int _currentInsight = 0;

  static const List<Map<String, String>> _insights = [
    {
      'icon': '🦠',
      'title': 'Diversité microbienne',
      'text':
          'Votre microbiome contient 847 espèces distinctes — 12 % au-dessus de la moyenne ouest-africaine. Une diversité élevée est associée à une meilleure résistance aux infections.',
    },
    {
      'icon': '🧠',
      'title': 'Axe intestin-cerveau',
      'text':
          '90 % de la sérotonine de votre corps est produite dans l\'intestin. Votre profil Lactobacillus reuteri est optimal, soutenant votre santé mentale et votre sommeil.',
    },
    {
      'icon': '🩸',
      'title': 'Risque métabolique',
      'text':
          'Votre ratio Firmicutes/Bacteroidetes (1,4) est dans la zone saine. Un ratio élevé (>2) est associé à +35 % de risque de diabète de type 2.',
    },
    {
      'icon': '🛡️',
      'title': 'Immunité microbienne',
      'text':
          'Votre niveau de Bifidobacterium (124 colonies) soutient activement vos lymphocytes T régulateurs — clé de la protection contre les inflammations chroniques.',
    },
  ];

  static const List<Map<String, dynamic>> _defaultRecs = [
    {
      'title': 'Fonio',
      'subtitle': 'Riche en méthionine, facilite la digestion',
      'emoji': '🌾',
      'score': 98
    },
    {
      'title': 'Feuilles de Baobab',
      'subtitle': 'Prébiotique naturel puissant',
      'emoji': '🌿',
      'score': 94
    },
    {
      'title': 'Niébé (haricots)',
      'subtitle': 'Fibres fermentescibles pour Bifidobacterium',
      'emoji': '🫘',
      'score': 91
    },
    {
      'title': 'Lait caillé fermenté',
      'subtitle': 'Probiotiques naturels adaptés',
      'emoji': '🥛',
      'score': 88
    },
    {
      'title': 'Arachides locales',
      'subtitle': 'Acides aminés essentiels',
      'emoji': '🥜',
      'score': 85
    },
    {
      'title': 'Pain de mil',
      'subtitle': 'Index glycémique bas, fibres solubles',
      'emoji': '🍞',
      'score': 82
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
    _startInsightRotation();
  }

  void _startInsightRotation() {
    Future.delayed(const Duration(seconds: 6), () {
      if (mounted) {
        setState(
            () => _currentInsight = (_currentInsight + 1) % _insights.length);
        _startInsightRotation();
      }
    });
  }

  Future<void> _loadRecommendations() async {
    try {
      final svc = RecommendationService();
      final response = await svc.getTodaysRecommendations();
      if (mounted) {
        setState(() {
          _recommendations = response['personalized'] ?? [];
          _isLoadingRec = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoadingRec = false);
    }
  }

  Future<void> _refresh() async {
    final p = Provider.of<MicrobiomeProvider>(context, listen: false);
    await p.loadDashboardScores();
    await _loadRecommendations();
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final micro = Provider.of<MicrobiomeProvider>(context);
    final user = auth.user;
    final scores = micro.dashboardScores;
    final firstName = user?['first_name'] ?? 'Utilisateur';

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedStage(
        child: SafeArea(
          child: RefreshIndicator(
            onRefresh: _refresh,
            color: AppColors.primary,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 20),
                    _buildHeader(firstName, user),
                    const SizedBox(height: 16),
                    const HeroBannerCard(
                      title: 'BiomeX Visual Intelligence',
                      subtitle:
                          'Suivi clinique enrichi avec vues nutritionnelles et contenus dynamiques',
                      imageUrl:
                          'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=1300&q=80',
                      badgeLabel: 'NOUVEAU',
                    ),
                    const SizedBox(height: 24),
                    _buildScoreCard(scores, micro.isLoading),
                    const SizedBox(height: 20),
                    _buildIndicatorPills(scores),
                    const SizedBox(height: 28),
                    _buildAlertBanner(scores),
                    const SizedBox(height: 20),
                    _buildInsightCarousel(),
                    const SizedBox(height: 24),
                    const MediaReelSection(),
                    const SizedBox(height: 28),
                    _buildRecommendationsSection(),
                    const SizedBox(height: 24),
                    _buildScienceSection(),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(String firstName, Map<String, dynamic>? user) {
    return Row(
      children: [
        CircleAvatar(
          radius: 22,
          backgroundColor: AppColors.primary.withOpacity(0.15),
          backgroundImage:
              user?['avatar'] != null ? NetworkImage(user!['avatar']) : null,
          child: user?['avatar'] == null
              ? const Icon(Icons.person, color: AppColors.primary, size: 24)
              : null,
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('BIENVENUE',
                style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textTertiary,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1)),
            Text('$firstName 👋',
                style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary)),
          ],
        ),
        const Spacer(),
        GestureDetector(
          onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Aucune nouvelle notification.'),
                duration: Duration(seconds: 2),
                backgroundColor: AppColors.primary,
              ),
            );
          },
          child: Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 8,
                      offset: const Offset(0, 2))
                ]),
            child: const Icon(Icons.notifications,
                color: AppColors.primary, size: 22),
          ),
        ),
      ],
    );
  }

  Widget _buildScoreCard(Map<String, dynamic>? scores, bool isLoading) {
    final score = scores?['overall_score'] ?? 0;
    final statusText = _statusLabel(scores?['status'] ?? 'no_data');
    final species = scores?['species_count'] ?? 847;
    final probiotics = scores?['probiotic_count'] ?? 124;
    final pathogen = scores?['pathogen_percentage'] ?? 12;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: const Color(0xFF1A4D2E),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
              color: const Color(0xFF1A4D2E).withOpacity(0.35),
              blurRadius: 20,
              offset: const Offset(0, 8))
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('SCORE MICROBIOME',
                  style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: Colors.white60,
                      letterSpacing: 1.2)),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                    color: const Color(0xFFD4A017).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8)),
                child: const Row(
                  children: [
                    Icon(Icons.verified, color: Color(0xFFD4A017), size: 14),
                    SizedBox(width: 4),
                    Text('IA Validée',
                        style: TextStyle(
                            color: Color(0xFFD4A017),
                            fontSize: 11,
                            fontWeight: FontWeight.w700)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Align(
            alignment: Alignment.centerLeft,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(20)),
              child: Text(statusText,
                  style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                      letterSpacing: 0.5)),
            ),
          ),
          const SizedBox(height: 20),
          isLoading
              ? const SizedBox(
                  height: 160,
                  child: Center(
                      child:
                          CircularProgressIndicator(color: Color(0xFFD4A017))))
              : SizedBox(
                  height: 160,
                  child: CustomPaint(
                    painter:
                        _ArcGaugePainter(value: score.toDouble(), max: 100),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(score > 0 ? '$score' : '-',
                              style: const TextStyle(
                                  fontSize: 52,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white)),
                          const Text('/100',
                              style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.white54,
                                  fontWeight: FontWeight.w500)),
                        ],
                      ),
                    ),
                  ),
                ),
          const SizedBox(height: 20),
          Divider(color: Colors.white.withOpacity(0.15), height: 1),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _statItem('ESPÈCES', '$species'),
              _vertDiv(),
              _statItem('PROBIOTIQUES', '$probiotics'),
              _vertDiv(),
              _statItem('PATHOGÈNES', '$pathogen%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _statItem(String label, String value) => Column(
        children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Colors.white54,
                  letterSpacing: 0.8)),
          const SizedBox(height: 4),
          Text(value,
              style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white)),
        ],
      );

  Widget _vertDiv() =>
      Container(width: 1, height: 32, color: Colors.white.withOpacity(0.15));

  Widget _buildIndicatorPills(Map<String, dynamic>? scores) {
    final diversity = scores?['diversity_score'] ?? 78;
    final inflammation = scores?['inflammation_score'] ?? 22;
    final gutBrain = scores?['gut_brain_score'] ?? 71;
    return Row(
      children: [
        Expanded(
            child: _pillCard(Icons.scatter_plot_outlined, 'DIVERSITÉ',
                '$diversity/100', AppColors.primary)),
        const SizedBox(width: 10),
        Expanded(
            child: _pillCard(
                Icons.local_fire_department_outlined,
                'INFLAMMATION',
                inflammation < 30
                    ? 'Faible'
                    : inflammation < 60
                        ? 'Modérée'
                        : 'Élevée',
                inflammation < 30 ? AppColors.success : AppColors.warning)),
        const SizedBox(width: 10),
        Expanded(
            child: _pillCard(
                Icons.psychology_outlined,
                'AXE CERVEAU',
                gutBrain > 60 ? 'Stable' : 'À surveiller',
                gutBrain > 60 ? AppColors.success : AppColors.warning)),
      ],
    );
  }

  Widget _pillCard(IconData icon, String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(children: [
        Icon(icon, size: 22, color: color),
        const SizedBox(height: 6),
        Text(label,
            style: const TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.w700,
                color: AppColors.textTertiary,
                letterSpacing: 0.5)),
        const SizedBox(height: 4),
        Text(value,
            style: TextStyle(
                fontSize: 13, fontWeight: FontWeight.bold, color: color),
            textAlign: TextAlign.center),
      ]),
    );
  }

  Widget _buildAlertBanner(Map<String, dynamic>? scores) {
    final score = scores?['overall_score'] ?? 78;
    if (score >= 70) return const SizedBox.shrink();
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3CD),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFD4A017).withOpacity(0.4)),
      ),
      child: Row(
        children: [
          const Text('⚠️', style: TextStyle(fontSize: 22)),
          const SizedBox(width: 12),
          const Expanded(
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Score en dessous du seuil optimal',
                  style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      color: Color(0xFF7D6008))),
              SizedBox(height: 2),
              Text(
                  'Consultez l\'écran Nutrition pour des recommandations adaptées à votre profil.',
                  style: TextStyle(fontSize: 11, color: Color(0xFF7D6008))),
            ],
          )),
        ],
      ),
    );
  }

  Widget _buildInsightCarousel() {
    final insight = _insights[_currentInsight];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('Insight du moment',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary)),
            const Spacer(),
            Row(
              children: List.generate(
                  _insights.length,
                  (i) => Container(
                        width: i == _currentInsight ? 20 : 6,
                        height: 6,
                        margin: const EdgeInsets.only(left: 4),
                        decoration: BoxDecoration(
                          color: i == _currentInsight
                              ? AppColors.primary
                              : AppColors.textTertiary.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(3),
                        ),
                      )),
            ),
          ],
        ),
        const SizedBox(height: 12),
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 500),
          child: Container(
            key: ValueKey(_currentInsight),
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2))
              ],
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(14)),
                  child: Center(
                      child: Text(insight['icon']!,
                          style: const TextStyle(fontSize: 26))),
                ),
                const SizedBox(width: 14),
                Expanded(
                    child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(insight['title']!,
                        style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary)),
                    const SizedBox(height: 5),
                    Text(insight['text']!,
                        style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                            height: 1.5)),
                  ],
                )),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Recommandations du jour',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary)),
            const Row(children: [
              Text('Voir tout',
                  style: TextStyle(
                      fontSize: 13,
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600)),
              SizedBox(width: 2),
              Icon(Icons.arrow_forward, size: 14, color: AppColors.primary),
            ]),
          ],
        ),
        const SizedBox(height: 14),
        SizedBox(
          height: 160,
          child: _isLoadingRec
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _recommendations.isNotEmpty
                      ? _recommendations.length
                      : _defaultRecs.length,
                  itemBuilder: (context, i) {
                    if (_recommendations.isNotEmpty) {
                      final r = _recommendations[i];
                      return _recCard(
                          r['title'] ?? '', r['description'] ?? '', '🌱', 90);
                    } else {
                      final r = _defaultRecs[i];
                      return _recCard(
                          r['title'] as String,
                          r['subtitle'] as String,
                          r['emoji'] as String,
                          r['score'] as int);
                    }
                  },
                ),
        ),
      ],
    );
  }

  Widget _recCard(String title, String subtitle, String emoji, int score) {
    return Container(
      width: 130,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(12)),
                child: Center(
                    child: Text(emoji, style: const TextStyle(fontSize: 26))),
              ),
              Positioned(
                top: 0,
                right: 0,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                  decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(8)),
                  child: Text('$score%',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 9,
                          fontWeight: FontWeight.w700)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(title,
              style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary),
              maxLines: 2,
              overflow: TextOverflow.ellipsis),
          const SizedBox(height: 3),
          Text(subtitle,
              style: const TextStyle(
                  fontSize: 10, color: AppColors.textTertiary, height: 1.3),
              maxLines: 2,
              overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }

  Widget _buildScienceSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('🔬 Le saviez-vous ?',
            style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary)),
        const SizedBox(height: 12),
        _factCard('🧬', '100 trillions',
            'de micro-organismes vivent dans votre intestin, codant 150× plus de gènes que votre génome humain.'),
        const SizedBox(height: 10),
        _factCard('🌍', 'Biais scientifique',
            '95 % des données microbiomiques mondiales viennent de populations occidentales. BiomeX corrige ce déséquilibre.'),
        const SizedBox(height: 10),
        _factCard('🥗', 'Aliments africains',
            'Le fonio, le niébé et les feuilles de baobab nourrissent des espèces bactériennes absentes des régimes occidentaux.'),
      ],
    );
  }

  Widget _factCard(String emoji, String title, String text) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 22)),
          const SizedBox(width: 12),
          Expanded(
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      color: AppColors.textPrimary)),
              const SizedBox(height: 3),
              Text(text,
                  style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                      height: 1.4)),
            ],
          )),
        ],
      ),
    );
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'excellent':
        return '✨ EXCELLENT';
      case 'tres_bon':
        return '✅ TRÈS BON';
      case 'bon':
        return '👍 BON';
      case 'a_ameliorer':
        return '⚠️ À AMÉLIORER';
      default:
        return '✅ TRÈS BON';
    }
  }
}

class _ArcGaugePainter extends CustomPainter {
  final double value;
  final double max;
  _ArcGaugePainter({required this.value, required this.max});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height * 0.6);
    final radius = size.width * 0.42;
    const startAngle = math.pi * 0.75;
    const sweepAngle = math.pi * 1.5;

    canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        false,
        Paint()
          ..color = Colors.white.withOpacity(0.15)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 14
          ..strokeCap = StrokeCap.round);
    canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle * (value / max).clamp(0.0, 1.0),
        false,
        Paint()
          ..color = const Color(0xFFD4A017)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 14
          ..strokeCap = StrokeCap.round);
  }

  @override
  bool shouldRepaint(covariant _ArcGaugePainter old) => old.value != value;
}
