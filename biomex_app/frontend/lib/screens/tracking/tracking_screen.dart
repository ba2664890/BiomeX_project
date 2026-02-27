import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../constants/app_theme.dart';
import '../../providers/tracking_provider.dart';
import '../../providers/microbiome_provider.dart';
import '../../widgets/animated_stage.dart';
import '../../widgets/hero_banner_card.dart';

class TrackingScreen extends StatefulWidget {
  const TrackingScreen({super.key});
  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int? _selectedWellness;
  int? _selectedRating;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final tp = Provider.of<TrackingProvider>(context, listen: false);
    final mp = Provider.of<MicrobiomeProvider>(context, listen: false);
    await Future.wait([tp.loadTrackingDashboard(), mp.loadScoreHistory()]);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tp = Provider.of<TrackingProvider>(context);
    final mp = Provider.of<MicrobiomeProvider>(context);
    final dashboard = tp.trackingDashboard;
    final scoreHistory = mp.scoreHistory;
    final currentScore = dashboard?['current_score'] ?? 78;
    final scoreChange = dashboard?['score_change'] ?? 12;
    final nextTestDays = dashboard?['next_test_days'] ?? 45;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedStage(
        child: SafeArea(
          child: Column(
            children: [
              // ── AppBar ──────────────────────────────────────────────
              Container(
                color: Colors.transparent,
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Expanded(
                            child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Suivi de Santé',
                                style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.textPrimary)),
                            Text('Évolution de votre microbiome dans le temps',
                                style: TextStyle(
                                    fontSize: 13,
                                    color: AppColors.textTertiary)),
                          ],
                        )),
                        Container(
                          width: 42,
                          height: 42,
                          decoration: BoxDecoration(
                              color: Colors.white,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                    color: Colors.black.withOpacity(0.06),
                                    blurRadius: 8)
                              ]),
                          child: const Icon(Icons.calendar_today_outlined,
                              color: AppColors.primary, size: 20),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const HeroBannerCard(
                      title: 'Tracking Live',
                      subtitle:
                          'Visualisation continue de vos indicateurs de progression',
                      imageUrl:
                          'https://images.unsplash.com/photo-1578496479763-13f9d9f20b84?auto=format&fit=crop&w=1200&q=80',
                      badgeLabel: 'TRACKING',
                    ),
                    const SizedBox(height: 14),
                    // Tabs
                    Container(
                      decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12)),
                      child: TabBar(
                        controller: _tabController,
                        indicator: BoxDecoration(
                            color: const Color(0xFF1A4D2E),
                            borderRadius: BorderRadius.circular(10)),
                        indicatorSize: TabBarIndicatorSize.tab,
                        labelColor: Colors.white,
                        unselectedLabelColor: AppColors.textSecondary,
                        labelStyle: const TextStyle(
                            fontSize: 12, fontWeight: FontWeight.w700),
                        tabs: const [
                          Tab(text: 'Score'),
                          Tab(text: 'Bien-être'),
                          Tab(text: 'Marqueurs')
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // ── Content ─────────────────────────────────────────────
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildScoreTab(
                        currentScore, scoreChange, scoreHistory, nextTestDays),
                    _buildWellnessTab(),
                    _buildMarkersTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── SCORE TAB ──────────────────────────────────────────────────────────────
  Widget _buildScoreTab(
      int score, int scoreChange, List<dynamic> history, int nextTestDays) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Main score card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 12,
                    offset: const Offset(0, 4))
              ]),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('SCORE MICROBIOME',
                      style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textTertiary,
                          letterSpacing: 1)),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                        color: AppColors.success.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('+$scoreChange pts',
                            style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: AppColors.success)),
                        const Text('vs période préc.',
                            style: TextStyle(
                                fontSize: 10, color: AppColors.success)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text('$score',
                      style: const TextStyle(
                          fontSize: 52,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary)),
                  const SizedBox(width: 4),
                  const Text('/100',
                      style: TextStyle(
                          fontSize: 18,
                          color: AppColors.textTertiary,
                          fontWeight: FontWeight.w500)),
                  const Spacer(),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                        color: const Color(0xFF1A4D2E),
                        borderRadius: BorderRadius.circular(12)),
                    child: const Text('TRÈS BON',
                        style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Colors.white)),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(height: 130, child: _buildLineChart(history, score)),
              const SizedBox(height: 8),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Jan',
                      style: TextStyle(
                          fontSize: 10, color: AppColors.textTertiary)),
                  Text('Fév',
                      style: TextStyle(
                          fontSize: 10, color: AppColors.textTertiary)),
                  Text('Mar',
                      style: TextStyle(
                          fontSize: 10, color: AppColors.textTertiary)),
                  Text('Avr',
                      style: TextStyle(
                          fontSize: 10, color: AppColors.textTertiary)),
                  Text('Mai',
                      style: TextStyle(
                          fontSize: 10,
                          color: AppColors.primary,
                          fontWeight: FontWeight.w600)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Score interpretation
        _buildScoreInterpretation(score),
        const SizedBox(height: 20),

        // Next test card
        _buildNextTestCard(nextTestDays),
        const SizedBox(height: 20),

        // Tips
        _buildImprovementTips(),
      ],
    );
  }

  Widget _buildLineChart(List<dynamic> history, int currentScore) {
    final spots = history.isNotEmpty
        ? history
            .asMap()
            .entries
            .map((e) => FlSpot(
                e.key.toDouble(), (e.value['overall_score'] ?? 0).toDouble()))
            .toList()
        : [
            const FlSpot(0, 55),
            const FlSpot(1, 58),
            const FlSpot(2, 63),
            const FlSpot(3, 68),
            const FlSpot(4, 78)
          ];

    return LineChart(LineChartData(
      gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (v) =>
              FlLine(color: Colors.grey.withOpacity(0.08), strokeWidth: 1)),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: false),
      lineBarsData: [
        LineChartBarData(
          spots: spots,
          isCurved: true,
          color: const Color(0xFF1A4D2E),
          barWidth: 3,
          dotData: FlDotData(
              show: true,
              getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
                    radius: spot.x == spots.last.x ? 5 : 3,
                    color: spot.x == spots.last.x
                        ? const Color(0xFFD4A017)
                        : const Color(0xFF1A4D2E),
                    strokeWidth: 2,
                    strokeColor: Colors.white,
                  )),
          belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(colors: [
                const Color(0xFF1A4D2E).withOpacity(0.15),
                Colors.transparent
              ], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
        )
      ],
    ));
  }

  Widget _buildScoreInterpretation(int score) {
    final bands = [
      {
        'label': 'À améliorer',
        'range': '0–50',
        'color': AppColors.error,
        'active': score < 50
      },
      {
        'label': 'Bon',
        'range': '50–70',
        'color': AppColors.warning,
        'active': score >= 50 && score < 70
      },
      {
        'label': 'Très bon',
        'range': '70–85',
        'color': AppColors.success,
        'active': score >= 70 && score < 85
      },
      {
        'label': 'Excellent',
        'range': '85–100',
        'color': const Color(0xFF1A4D2E),
        'active': score >= 85
      },
    ];
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)
          ]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Interprétation du score',
              style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary)),
          const SizedBox(height: 12),
          Row(
            children: bands
                .map((b) => Expanded(
                        child: Container(
                      margin: const EdgeInsets.only(right: 6),
                      padding: const EdgeInsets.symmetric(
                          vertical: 10, horizontal: 4),
                      decoration: BoxDecoration(
                        color: (b['active'] as bool)
                            ? (b['color'] as Color).withOpacity(0.15)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                            color: (b['active'] as bool)
                                ? b['color'] as Color
                                : Colors.grey.shade200),
                      ),
                      child: Column(
                        children: [
                          Text(b['label'] as String,
                              style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w700,
                                  color: (b['active'] as bool)
                                      ? b['color'] as Color
                                      : AppColors.textTertiary),
                              textAlign: TextAlign.center),
                          const SizedBox(height: 2),
                          Text(b['range'] as String,
                              style: TextStyle(
                                  fontSize: 10,
                                  color: (b['active'] as bool)
                                      ? b['color'] as Color
                                      : AppColors.textTertiary)),
                        ],
                      ),
                    )))
                .toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildNextTestCard(int days) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          color: const Color(0xFF1A4D2E),
          borderRadius: BorderRadius.circular(20)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('📦', style: TextStyle(fontSize: 22)),
              const SizedBox(width: 10),
              const Text('PROCHAIN TEST',
                  style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: Colors.white60,
                      letterSpacing: 1.2)),
            ],
          ),
          const SizedBox(height: 10),
          Text('Recommandé dans $days jours',
              style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white)),
          const SizedBox(height: 6),
          const Text(
              'Un suivi régulier (tous les 3 mois) permet de mesurer l\'impact de vos changements alimentaires sur votre microbiome.',
              style:
                  TextStyle(fontSize: 12, color: Colors.white60, height: 1.4)),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () async {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Commande en cours...')),
                );
                final mp =
                    Provider.of<MicrobiomeProvider>(context, listen: false);
                final res = await mp.requestNewKit();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).hideCurrentSnackBar();
                  if (res != null) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                            'Votre commande a été enregistrée avec succès.'),
                        backgroundColor: AppColors.success,
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content:
                            Text(mp.error ?? 'Erreur lors de la commande.'),
                        backgroundColor: AppColors.error,
                      ),
                    );
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD4A017),
                  foregroundColor: Colors.white,
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14))),
              child: const Text('Commander le kit BiomeX',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImprovementTips() {
    final tips = [
      {
        'icon': '🌾',
        'tip':
            'Intégrer 2 portions de fonio ou mil par semaine peut augmenter votre score de 3–5 points en un mois.'
      },
      {
        'icon': '🏃',
        'tip':
            '30 min de marche quotidienne augmente la diversité microbienne de 12% selon les études de cohortes africaines.'
      },
      {
        'icon': '💤',
        'tip':
            '7–9h de sommeil régulier stabilise l\'axe intestin-cerveau et réduit la cortisol pro-inflammatoire.'
      },
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Comment améliorer votre score ?',
            style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary)),
        const SizedBox(height: 12),
        ...tips.map((t) => Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                        color: Colors.black.withOpacity(0.04), blurRadius: 8)
                  ]),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(t['icon']!, style: const TextStyle(fontSize: 20)),
                  const SizedBox(width: 12),
                  Expanded(
                      child: Text(t['tip']!,
                          style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                              height: 1.4))),
                ],
              ),
            )),
      ],
    );
  }

  // ── WELLNESS TAB ────────────────────────────────────────────────────────────
  Widget _buildWellnessTab() {
    final categories = [
      {
        'emoji': '🏃',
        'label': 'Digestif',
        'color': const Color(0xFF3B82F6),
        'desc': 'Ballonnements, transit, douleurs'
      },
      {
        'emoji': '⚡',
        'label': 'Énergie',
        'color': const Color(0xFFF97316),
        'desc': 'Vitalité, fatigue chronique'
      },
      {
        'emoji': '🌙',
        'label': 'Sommeil',
        'color': const Color(0xFF8B5CF6),
        'desc': 'Qualité, durée, réveil'
      },
      {
        'emoji': '✨',
        'label': 'Peau',
        'color': const Color(0xFFEC4899),
        'desc': 'Acné, eczéma, teint'
      },
      {
        'emoji': '🧠',
        'label': 'Mental',
        'color': const Color(0xFF10B981),
        'desc': 'Humeur, concentration, stress'
      },
      {
        'emoji': '💪',
        'label': 'Physique',
        'color': const Color(0xFFEF4444),
        'desc': 'Douleurs, inflammation'
      },
    ];

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Comment vous sentez-vous ?',
            style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary)),
        const SizedBox(height: 6),
        const Text(
            'Ces données sont corrélées avec votre microbiome pour identifier des liens causaux.',
            style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 0.9,
          children: categories.asMap().entries.map((entry) {
            final i = entry.key;
            final cat = entry.value;
            final color = cat['color'] as Color;
            final selected = _selectedWellness == i;
            return GestureDetector(
              onTap: () => setState(() {
                _selectedWellness = selected ? null : i;
                _selectedRating = null;
              }),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: selected ? color.withOpacity(0.12) : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                      color: selected ? color : Colors.transparent, width: 2),
                  boxShadow: [
                    BoxShadow(
                        color: Colors.black.withOpacity(0.04), blurRadius: 8)
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                          color: color.withOpacity(0.1),
                          shape: BoxShape.circle),
                      child: Center(
                          child: Text(cat['emoji'] as String,
                              style: const TextStyle(fontSize: 22))),
                    ),
                    const SizedBox(height: 8),
                    Text(cat['label'] as String,
                        style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: selected ? color : AppColors.textPrimary)),
                    const SizedBox(height: 3),
                    Text(cat['desc'] as String,
                        style: const TextStyle(
                            fontSize: 9, color: AppColors.textTertiary),
                        textAlign: TextAlign.center),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        if (_selectedWellness != null) ...[
          const SizedBox(height: 20),
          _buildWellnessRating(categories[_selectedWellness!]),
        ],
        const SizedBox(height: 24),
        // Correlation info
        _buildCorrelationCard(),
      ],
    );
  }

  Widget _buildWellnessRating(Map<String, dynamic> cat) {
    final color = cat['color'] as Color;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          color: color.withOpacity(0.06),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Évaluer : ${cat['label']}',
              style: TextStyle(
                  fontSize: 15, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 14),
          const Text('Comment vous sentez-vous aujourd\'hui ?',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          Row(
            children: List.generate(5, (i) {
              final isSelected = _selectedRating == i;
              return Expanded(
                  child: GestureDetector(
                onTap: () => setState(() => _selectedRating = i),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? color.withOpacity(0.15)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                        color: isSelected ? color : Colors.transparent),
                  ),
                  child: Column(
                    children: [
                      Text(['😞', '😕', '😐', '🙂', '😊'][i],
                          style: const TextStyle(fontSize: 28)),
                      const SizedBox(height: 4),
                      Text(['Très mal', 'Mal', 'Moyen', 'Bien', 'Très bien'][i],
                          style: TextStyle(
                              fontSize: 8,
                              color:
                                  isSelected ? color : AppColors.textTertiary,
                              fontWeight: isSelected
                                  ? FontWeight.bold
                                  : FontWeight.normal),
                          textAlign: TextAlign.center),
                    ],
                  ),
                ),
              ));
            }),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _selectedRating == null
                  ? null
                  : () async {
                      final date =
                          DateTime.now().toIso8601String().split('T')[0];
                      final catLabel = cat['label'] as String;
                      final rating = _selectedRating! + 1; // 1 to 5

                      ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Enregistrement...')));

                      final tp =
                          Provider.of<TrackingProvider>(context, listen: false);
                      await tp.createWellnessCheck(
                          date: date, category: catLabel, rating: rating);

                      if (context.mounted) {
                        ScaffoldMessenger.of(context).hideCurrentSnackBar();
                        if (tp.error == null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content:
                                      Text('Bilan enregistré avec succès !'),
                                  backgroundColor: AppColors.success));
                          setState(() {
                            _selectedRating = null;
                            _selectedWellness = null;
                          });
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                              content: Text('Erreur: ${tp.error}'),
                              backgroundColor: AppColors.error));
                        }
                      }
                    },
              style: ElevatedButton.styleFrom(
                  backgroundColor: color,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12))),
              child: const Text('Enregistrer'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCorrelationCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
          color: const Color(0xFFE8F5E9),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.primary.withOpacity(0.2))),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(Icons.insights, color: AppColors.primary, size: 18),
            SizedBox(width: 8),
            Text('Corrélations identifiées par BiomeX IA',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primary)),
          ]),
          SizedBox(height: 10),
          Text(
              '• Votre faible niveau Akkermansia est corrélé avec des troubles digestifs légers — 78% de probabilité selon nos modèles.',
              style: TextStyle(
                  fontSize: 11, color: Color(0xFF2E7D32), height: 1.4)),
          SizedBox(height: 6),
          Text(
              '• Votre bon niveau Lactobacillus reuteri est associé à une meilleure qualité de sommeil chez les profils similaires.',
              style: TextStyle(
                  fontSize: 11, color: Color(0xFF2E7D32), height: 1.4)),
        ],
      ),
    );
  }

  // ── MARKERS TAB ─────────────────────────────────────────────────────────────
  Widget _buildMarkersTab() {
    final markers = [
      {
        'label': 'Diversité microbienne',
        'before': 0.62,
        'after': 0.78,
        'unit': '/100',
        'beforeVal': '62',
        'afterVal': '78'
      },
      {
        'label': 'Indice d\'inflammation',
        'before': 0.38,
        'after': 0.22,
        'unit': '/100',
        'beforeVal': '38',
        'afterVal': '22',
        'invert': true
      },
      {
        'label': 'Bifidobacterium',
        'before': 0.09,
        'after': 0.18,
        'unit': '% rel.',
        'beforeVal': '9%',
        'afterVal': '18%'
      },
      {
        'label': 'Ratio Firmicutes/Bacteroidetes',
        'before': 0.9,
        'after': 0.72,
        'unit': 'ratio',
        'beforeVal': '1,8',
        'afterVal': '1,4',
        'invert': true,
        'intScale': true
      },
      {
        'label': 'Akkermansia muciniphila',
        'before': 0.02,
        'after': 0.04,
        'unit': '% rel.',
        'beforeVal': '0.2%',
        'afterVal': '0.4%'
      },
      {
        'label': 'Score Axe Intestin-Cerveau',
        'before': 0.58,
        'after': 0.71,
        'unit': '/100',
        'beforeVal': '58',
        'afterVal': '71'
      },
    ];

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: const [
            Text('Comparaison des marqueurs',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary)),
            Text('Jan → Mai 2026',
                style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textTertiary,
                    fontWeight: FontWeight.w500)),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 12,
                    offset: const Offset(0, 4))
              ]),
          child: Column(
            children: markers.asMap().entries.map((entry) {
              final m = entry.value;
              final isLast = entry.key == markers.length - 1;
              final invert = m['invert'] == true;
              final before = m['before'] as double;
              final after = m['after'] as double;
              final improved = invert ? after < before : after > before;
              final color = improved ? AppColors.success : AppColors.error;
              final pctChange = ((after - before) / before * 100).abs().round();

              return Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                                child: Text(m['label'] as String,
                                    style: const TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: AppColors.textPrimary))),
                            Icon(
                                improved
                                    ? Icons.trending_up
                                    : Icons.trending_down,
                                size: 14,
                                color: color),
                            const SizedBox(width: 4),
                            Text('${improved ? '+' : '-'}$pctChange%',
                                style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: color)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Text('Avant ${m['beforeVal']}',
                                style: const TextStyle(
                                    fontSize: 10,
                                    color: AppColors.textTertiary)),
                            const Spacer(),
                            Text('Maintenant ${m['afterVal']} ${m['unit']}',
                                style: TextStyle(
                                    fontSize: 10,
                                    color: color,
                                    fontWeight: FontWeight.w600)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: after,
                            backgroundColor: Colors.grey.shade100,
                            valueColor: AlwaysStoppedAnimation<Color>(color),
                            minHeight: 8,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (!isLast) Divider(height: 1, color: Colors.grey.shade100),
                ],
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 20),
        // Science note
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF1A4D2E),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('🔬 Pourquoi ces marqueurs ?',
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.white)),
              SizedBox(height: 10),
              Text(
                  'Ces indicateurs sont issus de votre séquençage 16S rRNA et corrélés avec des données cliniques de cohortes africaines. Ils sont calculés par nos algorithmes Random Forest et XGBoost entraînés sur plus de 500 profils ouest-africains.',
                  style: TextStyle(
                      fontSize: 12, color: Colors.white70, height: 1.5)),
              SizedBox(height: 10),
              Text(
                  'Les modèles BiomeX sont entraînés sur des données africaines — une première mondiale pour des populations sous-représentées dans la recherche microbiomique mondiale (< 3 % des publications).',
                  style: TextStyle(
                      fontSize: 12, color: Colors.white60, height: 1.5)),
            ],
          ),
        ),
      ],
    );
  }
}
