import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../constants/app_theme.dart';
import '../../providers/nutrition_provider.dart';
import '../../widgets/animated_stage.dart';
import '../../widgets/hero_banner_card.dart';

class NutritionScreen extends StatefulWidget {
  const NutritionScreen({super.key});
  @override
  State<NutritionScreen> createState() => _NutritionScreenState();
}

class _NutritionScreenState extends State<NutritionScreen>
    with SingleTickerProviderStateMixin {
  final _searchController = TextEditingController();
  late TabController _tabController;

  // All African superfoods with scientific backing from the business plan
  static const List<Map<String, dynamic>> _allSuperfoods = [
    {
      'name': 'Fonio',
      'emoji': '🌾',
      'match': 98,
      'desc':
          'Céréale ancestrale riche en méthionine et cystéine. Favorise la croissance de Bifidobacterium grâce à ses fibres fermentescibles.',
      'nutrients': 'Protéines, Méthionine, Fibres',
      'effect': 'Diversité +12%',
      'color': 0xFFF5E6C8,
    },
    {
      'name': 'Feuilles de Baobab',
      'emoji': '🌿',
      'match': 94,
      'desc':
          'Prébiotique naturel puissant. 100g contiennent 6× plus de vitamine C que l\'orange. Nourrit sélectivement les Lactobacillus.',
      'nutrients': 'Vit. C, Calcium, Polyphénols',
      'effect': 'Bifidobacterium +18%',
      'color': 0xFFE8F5E9,
    },
    {
      'name': 'Niébé (haricot)',
      'emoji': '🫘',
      'match': 91,
      'desc':
          'Légumineuse locale riche en fibres solubles et résistantes. Principale source de prébiotiques dans les régimes sénégalais.',
      'nutrients': 'Fibres, Protéines végétales, Fer',
      'effect': 'AGCC +22%',
      'color': 0xFFF3E5F5,
    },
    {
      'name': 'Lait caillé fermenté',
      'emoji': '🥛',
      'match': 88,
      'desc':
          'Produit lactofermenté traditionnel. Source naturelle de Lactobacillus adaptés au profil génétique africain.',
      'nutrients': 'Probiotiques naturels, Calcium',
      'effect': 'Immunité +15%',
      'color': 0xFFE3F2FD,
    },
    {
      'name': 'Pain de mil / sorgho',
      'emoji': '🍞',
      'match': 85,
      'desc':
          'Index glycémique bas (IG 55 vs IG 70 blé). Fibres insolubles favorisant le transit et la production de butyrate.',
      'nutrients': 'Fibres insolubles, Magnésium, B3',
      'effect': 'Butyrate +10%',
      'color': 0xFFFFF3E0,
    },
    {
      'name': 'Arachides locales',
      'emoji': '🥜',
      'match': 82,
      'desc':
          'Source d\'acides aminés essentiels et d\'acide oléique. Les polyphénols des pellicules nourrissent Akkermansia muciniphila.',
      'nutrients': 'Protéines, AGI, Polyphénols',
      'effect': 'Akkermansia +8%',
      'color': 0xFFFFF8E1,
    },
    {
      'name': 'Gombo séché',
      'emoji': '🌱',
      'match': 79,
      'desc':
          'Mucilage unique protecteur de la muqueuse intestinale. Prébiotique naturel favorisant la colonisation par des bactéries bénéfiques.',
      'nutrients': 'Mucilage, Vit. K, Folates',
      'effect': 'Barrière intestinale +9%',
      'color': 0xFFE8F5E9,
    },
  ];

  static const List<Map<String, dynamic>> _foodsToAvoid = [
    {
      'name': 'Sucres raffinés',
      'emoji': '🍬',
      'reason': 'INFLAMMATOIRE',
      'detail':
          'Réduit la diversité microbienne de 30% en 2 semaines. Favorise Candida et bactéries pro-inflammatoires.'
    },
    {
      'name': 'Huiles de palme raffinée',
      'emoji': '🧴',
      'reason': 'DYSBIOSE',
      'detail':
          'Les acides gras saturés trans altèrent la composition microbienne et augmentent la perméabilité intestinale.'
    },
    {
      'name': 'Alcool',
      'emoji': '🍺',
      'reason': 'PERMÉABILITÉ',
      'detail':
          'Même à faibles doses, augmente le LPS sanguin (endotoxémie) par altération de la barrière intestinale.'
    },
    {
      'name': 'Viandes ultra-transformées',
      'emoji': '🌭',
      'reason': 'TMAO ÉLEVÉ',
      'detail':
          'La L-carnitine est convertie en TMAO pro-athérogène par certaines bactéries — risque cardiovasculaire.'
    },
  ];

  static const List<Map<String, dynamic>> _recipes = [
    {
      'name': 'Thiéboudienne au riz brun et légumes',
      'emoji': '🍲',
      'time': '45 min',
      'difficulty': 'Facile',
      'bio':
          'Le riz brun apporte 3× plus de fibres que le riz blanc. Associé au poisson, il optimise votre ratio Oméga-3/Oméga-6 pour réduire l\'inflammation.',
      'ingredients':
          'Riz brun, tilapia, carottes, aubergines, poivrons, tomate, oignons',
    },
    {
      'name': 'Bouillie de Mil fermentée au citron',
      'emoji': '🥣',
      'time': '20 min',
      'difficulty': 'Très facile',
      'bio':
          'La fermentation du mil pré-digère les phytates, améliorant l\'absorption du fer et du zinc de 40%. Parfait pour le petit-déjeuner microbiome-friendly.',
      'ingredients': 'Farine de mil, eau, sel, citron, miel local',
    },
    {
      'name': 'Soupe de niébé au gombo',
      'emoji': '🫘',
      'time': '35 min',
      'difficulty': 'Facile',
      'bio':
          'Combinaison synergique : les fibres du niébé + le mucilage du gombo créent une matrice prébiotique optimale pour vos Faecalibacterium prausnitzii.',
      'ingredients':
          'Niébé, gombo, tomate, oignons, piment doux, huile d\'arachide',
    },
    {
      'name': 'Smoothie baobab-citron-gingembre',
      'emoji': '🥤',
      'time': '5 min',
      'difficulty': 'Très facile',
      'bio':
          'Bombes prébiotiqueriche en polyphénols. La pulpe de baobab contient 10× plus de prébiotiques que la pomme. Le gingembre réduit l\'inflammation digestive.',
      'ingredients':
          'Pulpe de fruit du baobab, citron vert, gingembre frais, eau, miel',
    },
  ];

  List<Map<String, dynamic>> _filteredSuperfoods = List.from(_allSuperfoods);

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _searchController.addListener(_onSearch);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _onSearch() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      _filteredSuperfoods = _allSuperfoods
          .where((f) =>
              (f['name'] as String).toLowerCase().contains(query) ||
              (f['desc'] as String).toLowerCase().contains(query))
          .toList();
    });
  }

  Future<void> _loadData() async {
    final p = Provider.of<NutritionProvider>(context, listen: false);
    await p.loadAllData();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedStage(
        child: SafeArea(
          child: Column(
            children: [
              // ── Header + Search ─────────────────────────────────────
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
                            Text('Nutrition',
                                style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.textPrimary)),
                            Text('Adapté à votre microbiome africain',
                                style: TextStyle(
                                    fontSize: 13,
                                    color: AppColors.textTertiary)),
                          ],
                        )),
                        const Icon(Icons.auto_awesome,
                            color: Color(0xFFD4A017), size: 22),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const HeroBannerCard(
                      title: 'Nutrition Motion',
                      subtitle:
                          'Visualisez vos aliments clés avec des contenus immersifs',
                      imageUrl:
                          'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1200&q=80',
                      badgeLabel: 'NUTRITION',
                    ),
                    const SizedBox(height: 14),
                    _buildSearchBar(),
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
                          Tab(text: 'Super-aliments'),
                          Tab(text: 'À limiter'),
                          Tab(text: 'Recettes')
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
                    _buildSuperfoodsTab(),
                    _buildAvoidTab(),
                    _buildRecipesTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showLogFoodSheet(),
        backgroundColor: const Color(0xFFD4A017),
        elevation: 4,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      height: 48,
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 8,
                offset: const Offset(0, 2))
          ]),
      child: Row(
        children: [
          const SizedBox(width: 14),
          const Icon(Icons.search, color: AppColors.textTertiary, size: 20),
          const SizedBox(width: 10),
          Expanded(
              child: TextField(
            controller: _searchController,
            decoration: const InputDecoration(
                hintText: 'Rechercher un aliment local...',
                border: InputBorder.none,
                hintStyle:
                    TextStyle(color: AppColors.textTertiary, fontSize: 14),
                isDense: true),
          )),
          Container(
            width: 38,
            height: 38,
            margin: const EdgeInsets.only(right: 5),
            decoration: BoxDecoration(
                color: const Color(0xFF1A4D2E),
                borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.tune, color: Colors.white, size: 18),
          ),
        ],
      ),
    );
  }

  // ── SUPERFOODS TAB ─────────────────────────────────────────────────────────
  Widget _buildSuperfoodsTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Tip card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.primary.withOpacity(0.2))),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('💡', style: TextStyle(fontSize: 18)),
              SizedBox(width: 10),
              Expanded(
                  child: Text(
                      'Les aliments ci-dessous sont classés par compatibilité avec votre profil microbiomique. Le score % représente l\'affinité bactérienne estimée par notre IA.',
                      style: TextStyle(
                          fontSize: 12,
                          color: Color(0xFF2E7D32),
                          height: 1.4))),
            ],
          ),
        ),
        const SizedBox(height: 16),
        if (_filteredSuperfoods.isEmpty)
          const Center(
              child: Padding(
            padding: EdgeInsets.all(40),
            child: Text('Aucun aliment trouvé',
                style: TextStyle(color: AppColors.textTertiary)),
          ))
        else
          ..._filteredSuperfoods.map((food) => _superfoodDetailCard(food)),
      ],
    );
  }

  Widget _superfoodDetailCard(Map<String, dynamic> food) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 4))
          ]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            decoration: BoxDecoration(
                color: Color(food['color'] as int),
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(18))),
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Text(food['emoji'] as String,
                    style: const TextStyle(fontSize: 36)),
                const SizedBox(width: 16),
                Expanded(
                    child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(food['name'] as String,
                        style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary)),
                    const SizedBox(height: 4),
                    Text(food['nutrients'] as String,
                        style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.textSecondary,
                            fontWeight: FontWeight.w500)),
                  ],
                )),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('${food['match']}%',
                        style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary)),
                    const Text('compatibilité',
                        style: TextStyle(
                            fontSize: 9, color: AppColors.textTertiary)),
                    Container(
                      margin: const EdgeInsets.only(top: 4),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                          color: AppColors.success.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8)),
                      child: Text(food['effect'] as String,
                          style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: AppColors.success)),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Description
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(food['desc'] as String,
                style: const TextStyle(
                    fontSize: 13, color: AppColors.textSecondary, height: 1.5)),
          ),
        ],
      ),
    );
  }

  // ── AVOID TAB ──────────────────────────────────────────────────────────────
  Widget _buildAvoidTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
              color: const Color(0xFFFFF3F3),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.error.withOpacity(0.2))),
          child: const Text(
              '⚠️ Ces aliments perturbent spécifiquement les espèces bactériennes bénéfiques identifiées dans votre profil. Elle ne sont pas interdites, mais à consommer avec modération.',
              style: TextStyle(
                  fontSize: 12, color: Color(0xFFC62828), height: 1.4)),
        ),
        const SizedBox(height: 16),
        ..._foodsToAvoid.map((food) => _avoidCard(food)),
        const SizedBox(height: 20),
        // Transition nutritionnelle
        _buildTransitionCard(),
      ],
    );
  }

  Widget _avoidCard(Map<String, dynamic> food) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
        border: Border.all(color: const Color(0xFFFFDDDD)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
                color: const Color(0xFFFFF3F3),
                borderRadius: BorderRadius.circular(14)),
            child: Center(
                child: Text(food['emoji'] as String,
                    style: const TextStyle(fontSize: 28))),
          ),
          const SizedBox(width: 16),
          Expanded(
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(food['name'] as String,
                      style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary)),
                  const Spacer(),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                        color: const Color(0xFFFFE8E8),
                        borderRadius: BorderRadius.circular(8)),
                    child: Text(food['reason'] as String,
                        style: const TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            color: AppColors.error,
                            letterSpacing: 0.5)),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(food['detail'] as String,
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

  Widget _buildTransitionCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
            colors: [Color(0xFF1A4D2E), Color(0xFF2C6B42)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('📊 Transition Nutritionnelle',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white)),
          const SizedBox(height: 8),
          const Text(
              '+60 % de diabète et d\'obésité en Afrique entre 2010 et 2024 — principalement lié à l\'occidentalisation des régimes alimentaires. Votre profil microbiomique africain est optimisé pour les aliments traditionnels locaux.',
              style:
                  TextStyle(fontSize: 12, color: Colors.white70, height: 1.5)),
          const SizedBox(height: 16),
          const Text('Votre objectif hebdomadaire :',
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Colors.white)),
          const SizedBox(height: 10),
          _weeklyGoal('🌾', '2x / sem', 'Céréales ancestrales (fonio, mil)'),
          _weeklyGoal(
              '🫘', '3x / sem', 'Légumineuses locales (niébé, lentilles)'),
          _weeklyGoal('🥛', '1x / jour', 'Fermenté naturel (lait caillé)'),
          _weeklyGoal(
              '🌿', '1x / jour', 'Feuilles vertes locales (baobab, moringa)'),
        ],
      ),
    );
  }

  Widget _weeklyGoal(String emoji, String freq, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 16)),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
                color: const Color(0xFFD4A017).withOpacity(0.25),
                borderRadius: BorderRadius.circular(8)),
            child: Text(freq,
                style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFFD4A017))),
          ),
          const SizedBox(width: 8),
          Expanded(
              child: Text(label,
                  style: TextStyle(
                      fontSize: 12, color: Colors.white.withOpacity(0.8)))),
        ],
      ),
    );
  }

  // ── RECIPES TAB ────────────────────────────────────────────────────────────
  Widget _buildRecipesTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Recettes Microbiome-Friendly',
            style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary)),
        const SizedBox(height: 4),
        const Text(
            'Basées sur les aliments traditionnels africains — optimisées pour votre profil',
            style: TextStyle(fontSize: 12, color: AppColors.textTertiary)),
        const SizedBox(height: 16),
        ..._recipes.map((recipe) => _recipeDetailCard(recipe)),
      ],
    );
  }

  Widget _recipeDetailCard(Map<String, dynamic> recipe) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 4))
          ]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.08),
                        shape: BoxShape.circle),
                    child: Center(
                        child: Text(recipe['emoji'] as String,
                            style: const TextStyle(fontSize: 32)))),
                const SizedBox(width: 14),
                Expanded(
                    child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(recipe['name'] as String,
                        style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary)),
                    const SizedBox(height: 6),
                    Row(children: [
                      _chip(Icons.access_time, recipe['time'] as String,
                          AppColors.textTertiary),
                      const SizedBox(width: 8),
                      _chip(Icons.bar_chart, recipe['difficulty'] as String,
                          AppColors.success),
                    ]),
                  ],
                )),
              ],
            ),
          ),
          // Science note
          Container(
            margin: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(10)),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.science, size: 14, color: AppColors.primary),
                const SizedBox(width: 8),
                Expanded(
                    child: Text(recipe['bio'] as String,
                        style: const TextStyle(
                            fontSize: 11,
                            color: Color(0xFF2E7D32),
                            height: 1.4))),
              ],
            ),
          ),
          // Ingredients
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.restaurant_menu_outlined,
                    size: 14, color: AppColors.textTertiary),
                const SizedBox(width: 8),
                Expanded(
                    child: Text(recipe['ingredients'] as String,
                        style: const TextStyle(
                            fontSize: 12, color: AppColors.textSecondary))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _chip(IconData icon, String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: color),
        const SizedBox(width: 4),
        Text(label,
            style: TextStyle(
                fontSize: 11, color: color, fontWeight: FontWeight.w500)),
      ],
    );
  }

  void _showLogFoodSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Ajouter un aliment',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            const Text('Quelle catégorie ?',
                style: TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 12),
            ...[
              ['🌾', 'Céréale / Grain'],
              ['🥗', 'Légume / Feuille'],
              ['🍳', 'Plat cuisiné'],
              ['🥛', 'Fermenté'],
              ['💊', 'Complément']
            ].map((item) => ListTile(
                  leading: Text(item[0], style: const TextStyle(fontSize: 24)),
                  title: Text(item[1]),
                  trailing: const Icon(Icons.chevron_right,
                      color: AppColors.textTertiary),
                  onTap: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                            '${item[1]} ajouté à votre journal avec succès.'),
                        backgroundColor: const Color(0xFF1A4D2E),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                )),
          ],
        ),
      ),
    );
  }
}
