import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../constants/app_theme.dart';
import '../../providers/microbiome_provider.dart';
import '../../widgets/animated_stage.dart';
import '../../widgets/hero_banner_card.dart';

class ReportScreen extends StatefulWidget {
  const ReportScreen({super.key});
  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final p = Provider.of<MicrobiomeProvider>(context, listen: false);
    await Future.wait([
      p.loadLatestAnalysis(),
      p.loadBacteriaBalance(),
      p.loadHealthMarkers(),
      p.loadScoreHistory(),
    ]);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final micro = Provider.of<MicrobiomeProvider>(context);
    final analysis = micro.latestAnalysis;
    final scoreHistory = micro.scoreHistory;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedStage(
        child: SafeArea(
          child: Column(
            children: [
              // ── Header ─────────────────────────────────────────────
              Container(
                color: Colors.transparent,
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Rapport d\'Analyse',
                        style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary)),
                    const SizedBox(height: 4),
                    Text(
                      analysis != null
                          ? 'Analyse du ${_formatDate(analysis['created_at'])}'
                          : 'Dernière analyse disponible',
                      style: const TextStyle(
                          fontSize: 14, color: AppColors.textTertiary),
                    ),
                    const SizedBox(height: 14),
                    const HeroBannerCard(
                      title: 'Analyse Visuelle',
                      subtitle:
                          'Lecture dynamique de vos tendances microbiomiques',
                      imageUrl:
                          'https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=1200&q=80',
                      badgeLabel: 'REPORT',
                    ),
                    const SizedBox(height: 14),
                    // Tab bar
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
                          Tab(text: 'Vue d\'ensemble'),
                          Tab(text: 'Bactéries'),
                          Tab(text: 'Impact Santé'),
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
                    _buildOverviewTab(analysis, scoreHistory, micro),
                    _buildBacteriaTab(micro),
                    _buildHealthImpactTab(micro),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── OVERVIEW TAB ───────────────────────────────────────────────────────────
  Widget _buildOverviewTab(Map<String, dynamic>? analysis,
      List<dynamic> scoreHistory, MicrobiomeProvider micro) {
    final score = analysis?['overall_score'] ?? 78;
    final diversity = analysis?['diversity_score'] ?? 78;
    final inflammation = analysis?['inflammation_score'] ?? 22;

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Score history chart
        _buildScoreHistoryCard(scoreHistory, score),
        const SizedBox(height: 20),

        // Diversity indices
        _buildDiversityCard(analysis),
        const SizedBox(height: 20),

        // Risk meters
        _buildRiskAssessmentCard(score, inflammation, diversity),
        const SizedBox(height: 20),

        // Key metrics grid
        _buildMetricsGrid(analysis),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildScoreHistoryCard(List<dynamic> history, int currentScore) {
    final spots = history.isNotEmpty
        ? history
            .asMap()
            .entries
            .map((e) => FlSpot(
                e.key.toDouble(), (e.value['overall_score'] ?? 0).toDouble()))
            .toList()
        : [
            const FlSpot(0, 55),
            const FlSpot(1, 60),
            const FlSpot(2, 65),
            const FlSpot(3, 70),
            const FlSpot(4, 75),
            const FlSpot(5, 78)
          ];

    return Container(
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
              const Text('Évolution du Score',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary)),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8)),
                child: Text('$currentScore/100',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppColors.success)),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text('6 derniers mois',
              style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
          const SizedBox(height: 20),
          SizedBox(
            height: 140,
            child: LineChart(LineChartData(
              gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (v) => FlLine(
                      color: Colors.grey.withOpacity(0.08), strokeWidth: 1)),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 32,
                        getTitlesWidget: (v, m) => Text('${v.toInt()}',
                            style: const TextStyle(
                                fontSize: 10, color: AppColors.textTertiary)))),
                rightTitles:
                    AxisTitles(sideTitles: SideTitles(showTitles: false)),
                topTitles:
                    AxisTitles(sideTitles: SideTitles(showTitles: false)),
                bottomTitles:
                    AxisTitles(sideTitles: SideTitles(showTitles: false)),
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
                          radius: 4,
                          color: spot.x == spots.last.x
                              ? const Color(0xFFD4A017)
                              : const Color(0xFF1A4D2E),
                          strokeWidth: 2,
                          strokeColor: Colors.white)),
                  belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                          colors: [
                            const Color(0xFF1A4D2E).withOpacity(0.12),
                            Colors.transparent
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter)),
                )
              ],
            )),
          ),
        ],
      ),
    );
  }

  Widget _buildDiversityCard(Map<String, dynamic>? analysis) {
    final shannon = (analysis?['shannon_index'] ?? 3.8).toDouble();
    final chao1 = analysis?['chao1_index'] ?? 847;
    final simpson = (analysis?['simpson_index'] ?? 0.91).toDouble();
    final brayCurtis = (analysis?['bray_curtis'] ?? 0.24).toDouble();

    return Container(
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
          const Row(
            children: [
              Icon(Icons.biotech, color: AppColors.primary, size: 20),
              SizedBox(width: 8),
              Text('Indices de Diversité',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary)),
            ],
          ),
          const SizedBox(height: 6),
          const Text('Mesures alpha et bêta de votre microbiome',
              style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(
                child: _indexCard(
                    'Indice Shannon',
                    '${shannon.toStringAsFixed(1)}',
                    'Diversité globale\n(optimal > 3.5)',
                    shannon >= 3.5 ? AppColors.success : AppColors.warning)),
            const SizedBox(width: 12),
            Expanded(
                child: _indexCard(
                    'Richesse Chao1',
                    '$chao1',
                    'Espèces estimées\n(optimal > 600)',
                    chao1 >= 600 ? AppColors.success : AppColors.warning)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(
                child: _indexCard(
                    'Simpson',
                    '${simpson.toStringAsFixed(2)}',
                    'Équitabilité\n(optimal > 0.85)',
                    simpson >= 0.85 ? AppColors.success : AppColors.warning)),
            const SizedBox(width: 12),
            Expanded(
                child: _indexCard(
                    'Bray-Curtis',
                    '${brayCurtis.toStringAsFixed(2)}',
                    'Dist. population\n(faible = proche)',
                    brayCurtis <= 0.35
                        ? AppColors.success
                        : AppColors.warning)),
          ]),
        ],
      ),
    );
  }

  Widget _indexCard(String name, String value, String desc, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
          color: color.withOpacity(0.06),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.2))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value,
              style: TextStyle(
                  fontSize: 22, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(name,
              style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary)),
          const SizedBox(height: 2),
          Text(desc,
              style: TextStyle(fontSize: 10, color: color, height: 1.35)),
        ],
      ),
    );
  }

  Widget _buildRiskAssessmentCard(int score, int inflammation, int diversity) {
    final diabeteRisk = 100 - diversity - (score ~/ 2);
    final obesiteRisk = inflammation + (100 - score) ~/ 3;
    final cardioRisk = inflammation ~/ 2 + (100 - score) ~/ 4;

    return Container(
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
          const Row(
            children: [
              Icon(Icons.health_and_safety_outlined,
                  color: AppColors.primary, size: 20),
              SizedBox(width: 8),
              Text('Évaluation des Risques',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary)),
            ],
          ),
          const SizedBox(height: 4),
          const Text('Basé sur votre profil microbiomique',
              style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
          const SizedBox(height: 16),
          _riskBar('Diabète de type 2', diabeteRisk.clamp(0, 100),
              'Ratio Firmicutes/Bacteroidetes: 1.4'),
          const SizedBox(height: 14),
          _riskBar('Obésité / Surpoids', obesiteRisk.clamp(0, 100),
              'Faible extraction énergétique anormale'),
          const SizedBox(height: 14),
          _riskBar('Maladies cardiovasculaires', cardioRisk.clamp(0, 100),
              'TMAO: niveau normal dans votre profil'),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(12)),
            child: const Row(
              children: [
                Icon(Icons.info_outline, color: AppColors.success, size: 16),
                SizedBox(width: 8),
                Expanded(
                    child: Text(
                        'Ces estimations sont basées sur des corrélations microbiomiques. Consultez un médecin pour tout risque élevé.',
                        style:
                            TextStyle(fontSize: 10, color: AppColors.success))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _riskBar(String label, int risk, String detail) {
    final color = risk < 25
        ? AppColors.success
        : risk < 50
            ? AppColors.warning
            : AppColors.error;
    final riskLabel = risk < 25
        ? 'FAIBLE'
        : risk < 50
            ? 'MODÉRÉ'
            : 'ÉLEVÉ';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label,
                style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8)),
              child: Text(riskLabel,
                  style: TextStyle(
                      fontSize: 10, fontWeight: FontWeight.w700, color: color)),
            ),
          ],
        ),
        const SizedBox(height: 5),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: risk / 100,
            backgroundColor: Colors.grey.shade100,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
        const SizedBox(height: 3),
        Text(detail,
            style:
                const TextStyle(fontSize: 10, color: AppColors.textTertiary)),
      ],
    );
  }

  Widget _buildMetricsGrid(Map<String, dynamic>? analysis) {
    final metrics = [
      {
        'label': 'pH Intestinal',
        'value': '6.8',
        'unit': 'optimal',
        'icon': '⚗️',
        'ok': true
      },
      {
        'label': 'Ratio F/B',
        'value': '1.4',
        'unit': 'sain < 2',
        'icon': '⚖️',
        'ok': true
      },
      {
        'label': 'AGCC',
        'value': 'Élevé',
        'unit': 'butyrate+',
        'icon': '🔋',
        'ok': true
      },
      {
        'label': 'Perméabilité',
        'value': 'Faible',
        'unit': 'barrière OK',
        'icon': '🛡️',
        'ok': true
      },
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Marqueurs Clés',
            style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary)),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.8,
          children: metrics
              .map((m) => Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 8)
                        ]),
                    child: Row(
                      children: [
                        Text(m['icon'] as String,
                            style: const TextStyle(fontSize: 24)),
                        const SizedBox(width: 10),
                        Expanded(
                            child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(m['label'] as String,
                                style: const TextStyle(
                                    fontSize: 10,
                                    color: AppColors.textTertiary,
                                    fontWeight: FontWeight.w600)),
                            Text(m['value'] as String,
                                style: const TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.textPrimary)),
                            Text(m['unit'] as String,
                                style: TextStyle(
                                    fontSize: 9,
                                    color: (m['ok'] as bool)
                                        ? AppColors.success
                                        : AppColors.error,
                                    fontWeight: FontWeight.w600)),
                          ],
                        )),
                      ],
                    ),
                  ))
              .toList(),
        ),
      ],
    );
  }

  // ── BACTERIA TAB ────────────────────────────────────────────────────────────
  Widget _buildBacteriaTab(MicrobiomeProvider micro) {
    final balance = micro.bacteriaBalance;
    final defaultBacteria = [
      {
        'name': 'Bifidobacterium',
        'phylum': 'Actinobacteria',
        'pct': 18.4,
        'status': 'optimal',
        'role':
            'Immunité, production d\'acide lactique, protection barrière intestinale'
      },
      {
        'name': 'Lactobacillus',
        'phylum': 'Firmicutes',
        'pct': 12.6,
        'status': 'optimal',
        'role': 'Synthèse vitamines B, inhibition pathogènes, production AGCC'
      },
      {
        'name': 'Faecalibacterium prausnitzii',
        'phylum': 'Firmicutes',
        'pct': 10.2,
        'status': 'optimal',
        'role':
            'Anti-inflammatoire puissant, production butyrate — protecteur MICI'
      },
      {
        'name': 'Akkermansia muciniphila',
        'phylum': 'Verrucomicrobia',
        'pct': 3.8,
        'status': 'faible',
        'role':
            'Protection barrière mucosale, métabolisme — souvent réduit par alimentation industrielle'
      },
      {
        'name': 'Prevotella copri',
        'phylum': 'Bacteroidetes',
        'pct': 8.1,
        'status': 'optimal',
        'role':
            'Fermentation des fibres végétales, abondant dans les populations africaines rurales'
      },
      {
        'name': 'Bacteroides fragilis',
        'phylum': 'Bacteroidetes',
        'pct': 15.3,
        'status': 'optimal',
        'role':
            'Digestion des polysaccharides complexes, équilibre immunologique'
      },
      {
        'name': 'Clostridium difficile',
        'phylum': 'Firmicutes',
        'pct': 0.3,
        'status': 'normal',
        'role':
            'Présent en faibles quantités — normal. Une prolifération indique une dysbiose sévère'
      },
      {
        'name': 'Escherichia coli (commensal)',
        'phylum': 'Proteobacteria',
        'pct': 1.8,
        'status': 'normal',
        'role': 'Souche non pathogène — commensal normal. Synthèse vitamine K2'
      },
    ];

    final displayBacteria = balance.isNotEmpty ? balance : defaultBacteria;

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Composition pie summary
        _buildPhylumComposition(),
        const SizedBox(height: 20),

        // Bacteria list
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Espèces Identifiées',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary)),
              const SizedBox(height: 4),
              const Text('Séquençage 16S rRNA — Région V3-V4',
                  style:
                      TextStyle(fontSize: 12, color: AppColors.textTertiary)),
              const SizedBox(height: 14),
              ...displayBacteria.map((b) => _bacteriaItem(
                    name: b['name'] as String,
                    phylum: b['phylum'] as String,
                    pct: (b['pct'] as num).toDouble(),
                    status: b['status'] as String,
                    role: b['role'] as String,
                  )),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Probiotic focus
        _buildProbioticFocusCard(),
      ],
    );
  }

  Widget _buildPhylumComposition() {
    final phylums = [
      {'name': 'Firmicutes', 'pct': 48.2, 'color': const Color(0xFF1A4D2E)},
      {'name': 'Bacteroidetes', 'pct': 28.7, 'color': const Color(0xFFD4A017)},
      {'name': 'Actinobacteria', 'pct': 14.1, 'color': const Color(0xFF4CAF50)},
      {'name': 'Proteobacteria', 'pct': 5.2, 'color': const Color(0xFF2196F3)},
      {'name': 'Autres', 'pct': 3.8, 'color': const Color(0xFFBDBDBD)},
    ];

    return Container(
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
          const Text('Composition par Phylum',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary)),
          const SizedBox(height: 4),
          const Text('Ratio Firmicutes/Bacteroidetes : 1,68 (sain < 2)',
              style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
          const SizedBox(height: 16),
          ...phylums.map((p) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(children: [
                          Container(
                              width: 10,
                              height: 10,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                  color: p['color'] as Color,
                                  shape: BoxShape.circle)),
                          Text(p['name'] as String,
                              style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: AppColors.textPrimary)),
                        ]),
                        Text('${(p['pct'] as double).toStringAsFixed(1)} %',
                            style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: p['color'] as Color)),
                      ],
                    ),
                    const SizedBox(height: 5),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: (p['pct'] as double) / 100,
                        backgroundColor: Colors.grey.shade100,
                        valueColor:
                            AlwaysStoppedAnimation<Color>(p['color'] as Color),
                        minHeight: 7,
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _bacteriaItem(
      {required String name,
      required String phylum,
      required double pct,
      required String status,
      required String role}) {
    final statusColor = status == 'optimal'
        ? AppColors.success
        : status == 'faible'
            ? AppColors.warning
            : AppColors.textTertiary;
    final statusLabel = status == 'optimal'
        ? 'OPTIMAL'
        : status == 'faible'
            ? 'FAIBLE'
            : 'NORMAL';

    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      childrenPadding: EdgeInsets.zero,
      title: Row(
        children: [
          Expanded(
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name,
                  style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                      fontStyle: FontStyle.italic)),
              Text(phylum,
                  style: const TextStyle(
                      fontSize: 11, color: AppColors.textTertiary)),
            ],
          )),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('${pct.toStringAsFixed(1)} %',
                  style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: statusColor)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(6)),
                child: Text(statusLabel,
                    style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                        color: statusColor)),
              ),
            ],
          ),
        ],
      ),
      children: [
        Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
              color: statusColor.withOpacity(0.05),
              borderRadius: BorderRadius.circular(10)),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.science_outlined,
                  size: 14, color: AppColors.textTertiary),
              const SizedBox(width: 8),
              Expanded(
                  child: Text(role,
                      style: const TextStyle(
                          fontSize: 11,
                          color: AppColors.textSecondary,
                          height: 1.4))),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildProbioticFocusCard() {
    final probiotics = [
      {
        'name': 'Lactobacillus acidophilus',
        'food': 'Lait caillé fermenté, yaourt local',
        'benefit': 'Digestion du lactose, immunité'
      },
      {
        'name': 'Bifidobacterium longum',
        'food': 'Feuilles de baobab (prébiotique)',
        'benefit': 'Anxiété, côlon irritable'
      },
      {
        'name': 'Lactobacillus plantarum',
        'food': 'Légumes fermentés, niébé cuit',
        'benefit': 'Perméabilité intestinale'
      },
    ];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A4D2E),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Text('🦠', style: TextStyle(fontSize: 20)),
              SizedBox(width: 10),
              Text('Focus Probiotiques Africains',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white)),
            ],
          ),
          const SizedBox(height: 4),
          const Text('Souches adaptées à votre profil et aux aliments locaux',
              style: TextStyle(fontSize: 12, color: Colors.white60)),
          const SizedBox(height: 16),
          ...probiotics.map((p) => Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12)),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(p['name']!,
                        style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            fontStyle: FontStyle.italic)),
                    const SizedBox(height: 6),
                    Row(children: [
                      const Icon(Icons.restaurant,
                          color: Color(0xFFD4A017), size: 13),
                      const SizedBox(width: 6),
                      Expanded(
                          child: Text(p['food']!,
                              style: const TextStyle(
                                  fontSize: 11, color: Color(0xFFD4A017)))),
                    ]),
                    const SizedBox(height: 3),
                    Row(children: [
                      const Icon(Icons.check_circle_outline,
                          color: Colors.white60, size: 13),
                      const SizedBox(width: 6),
                      Expanded(
                          child: Text(p['benefit']!,
                              style: const TextStyle(
                                  fontSize: 11, color: Colors.white70))),
                    ]),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  // ── HEALTH IMPACT TAB ──────────────────────────────────────────────────────
  Widget _buildHealthImpactTab(MicrobiomeProvider micro) {
    final impacts = [
      {
        'icon': '⚡',
        'title': 'Métabolisme Énergétique',
        'score': 82,
        'color': const Color(0xFFF97316),
        'summary':
            'Vos bactéries fermentent efficacement les fibres en AGCC (butyrate, propionate, acétate) — source d\'énergie pour vos cellules intestinales et régulateur glycémique.',
        'details': [
          'Butyrate : niveau optimal → cellules coliques nourries',
          'Propionate : signal de satiété hépatique actif',
          'Acétate : substrat energétique musculaire disponible'
        ],
      },
      {
        'icon': '🛡️',
        'title': 'Immunité & Inflammation',
        'score': 76,
        'color': const Color(0xFF3B82F6),
        'summary':
            'Votre microbiome module activement vos lymphocytes T régulateurs. L\'inflammation de bas grade est bien contrôlée grâce à votre niveau élevé de Faecalibacterium prausnitzii.',
        'details': [
          'CRP estimée : basse (< 1 mg/L)',
          'IL-10 (anti-inflammatoire) : stimulus actif',
          'Dysbiose inflammatoire : absente'
        ],
      },
      {
        'icon': '🧠',
        'title': 'Axe Intestin-Cerveau',
        'score': 71,
        'color': const Color(0xFF8B5CF6),
        'summary':
            '90 % de la sérotonine est produite dans l\'intestin. Votre profil Lactobacillus reuteri et Bifidobacterium soutient la production de neurotransmetteurs et la qualité du sommeil.',
        'details': [
          'Sérotonine intestinale : production estimée normale',
          'GABA : précurseurs présents (L. rhamnosus)',
          'Axe vagal : signaux ascendants physiologiques'
        ],
      },
      {
        'icon': '🔒',
        'title': 'Barrière Intestinale',
        'score': 85,
        'color': const Color(0xFF10B981),
        'summary':
            'L\'intégrité de votre muqueuse intestinale est bonne. Akkermansia muciniphila est légèrement bas — un apport en polyphénols (thé vert, grenadine) peut améliorer ce marqueur.',
        'details': [
          'Jonctions serrées : intégrité estimée normale',
          'Mucus : couche protectrice active',
          'LPS sanguin (endotoxémie) : faible perméabilité'
        ],
      },
      {
        'icon': '💊',
        'title': 'Métabolisme Médicamenteux',
        'score': 68,
        'color': const Color(0xFFEC4899),
        'summary':
            'Votre microbiome biotransforme de nombreux médicaments. Ce score influence comment votre corps absorbe certains traitements — information pertinente pour votre médecin.',
        'details': [
          'Enzymes bêta-glucuronidases : niveau modéré',
          'Métabolisme des statines : adapté',
          'Réponse aux antibiotiques : profil à préserver'
        ],
      },
    ];

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.primary.withOpacity(0.2))),
          child: const Text(
              '📊 Ces estimations sont dérivées de votre profil bactérien par nos algorithmes IA entraînés sur des cohortes africaines. Ils ne remplacent pas un bilan médical.',
              style: TextStyle(
                  fontSize: 12, color: Color(0xFF2E7D32), height: 1.4)),
        ),
        const SizedBox(height: 16),
        ...impacts.map((impact) => _healthImpactCard(impact)).toList(),
      ],
    );
  }

  Widget _healthImpactCard(Map<String, dynamic> impact) {
    final score = impact['score'] as int;
    final color = impact['color'] as Color;
    final details = impact['details'] as List<String>;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 12,
                offset: const Offset(0, 4))
          ]),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        childrenPadding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
        title: Row(
          children: [
            Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                    color: color.withOpacity(0.1), shape: BoxShape.circle),
                child: Center(
                    child: Text(impact['icon'] as String,
                        style: const TextStyle(fontSize: 22)))),
            const SizedBox(width: 14),
            Expanded(
                child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(impact['title'] as String,
                    style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary)),
                const SizedBox(height: 4),
                Row(children: [
                  Expanded(
                      child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                        value: score / 100,
                        backgroundColor: Colors.grey.shade100,
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                        minHeight: 6),
                  )),
                  const SizedBox(width: 10),
                  Text('$score%',
                      style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: color)),
                ]),
              ],
            )),
          ],
        ),
        children: [
          Text(impact['summary'] as String,
              style: const TextStyle(
                  fontSize: 12, color: AppColors.textSecondary, height: 1.5)),
          const SizedBox(height: 12),
          ...details.map((d) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.check_circle, size: 14, color: color),
                      const SizedBox(width: 8),
                      Expanded(
                          child: Text(d,
                              style: const TextStyle(
                                  fontSize: 11, color: AppColors.textPrimary))),
                    ]),
              )),
        ],
      ),
    );
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return 'date inconnue';
    try {
      final d = DateTime.parse(dateStr);
      const months = [
        'jan.',
        'fév.',
        'mar.',
        'avr.',
        'mai',
        'juin',
        'juil.',
        'août',
        'sep.',
        'oct.',
        'nov.',
        'déc.'
      ];
      return '${d.day} ${months[d.month - 1]} ${d.year}';
    } catch (_) {
      return dateStr;
    }
  }
}
