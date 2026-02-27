import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/animated_stage.dart';
import '../../widgets/hero_banner_card.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _shareWithDoctor = true;
  bool _participateInResearch = false;

  String _safeStr(dynamic v, String fallback) {
    if (v == null) return fallback;
    if (v is String) return v;
    if (v is List) return v.join(', ');
    return v.toString();
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;
    final firstName = _safeStr(user?['first_name'], 'Aminata');
    final lastName = _safeStr(user?['last_name'], 'Fall');
    final city = _safeStr(user?['city'], 'Dakar, Plateau');
    final age = _safeStr(user?['age'], '28');
    final weight = _safeStr(user?['weight'], '64');
    final prefs = _safeStr(user?['dietary_preferences'], 'Halal, Végétarien');
    final allergies = _safeStr(user?['allergies'], 'Arachides (légères)');

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedStage(
        child: SafeArea(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const SizedBox(height: 16),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20),
                  child: HeroBannerCard(
                    title: 'Profil Dynamique',
                    subtitle:
                        'Préférences, confidentialité et suivi personnel en un seul espace',
                    imageUrl:
                        'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80',
                    badgeLabel: 'PROFILE',
                  ),
                ),
                const SizedBox(height: 26),

                // ── Avatar + Edit ─────────────────────────────────────
                _buildAvatar(user),
                const SizedBox(height: 16),

                // ── Name ──────────────────────────────────────────────
                Text(
                  '$firstName $lastName'.trim().isEmpty
                      ? 'Mon Profil'
                      : '$firstName $lastName'.trim(),
                  style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A1A2E)),
                ),
                const SizedBox(height: 6),

                // ── Location ──────────────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.location_on,
                        size: 13, color: Color(0xFF9E9E9E)),
                    const SizedBox(width: 3),
                    Text(city,
                        style: const TextStyle(
                            fontSize: 13, color: Color(0xFF9E9E9E))),
                  ],
                ),
                const SizedBox(height: 14),

                // ── Premium badge ─────────────────────────────────────
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border:
                        Border.all(color: const Color(0xFFDDDDDD), width: 1),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.verified_user,
                          size: 15, color: Color(0xFF1A4D2E)),
                      SizedBox(width: 6),
                      Text('BIOMEX PREMIUM',
                          style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF1A4D2E),
                              letterSpacing: 0.5)),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // ── Profil Biologique ─────────────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Padding(
                        padding: EdgeInsets.only(left: 4, bottom: 12),
                        child: Text('PROFIL BIOLOGIQUE',
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFFAAAAAA),
                                letterSpacing: 1.5)),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: const Color(0xFFEEEEEE), width: 1),
                        ),
                        child: Column(
                          children: [
                            _bioRow(Icons.calendar_month_outlined, 'Âge',
                                age == '—' ? '28 ans' : '$age ans'),
                            _divider(),
                            _bioRow(Icons.scale_outlined, 'Poids',
                                weight == '—' ? '64 kg' : '$weight kg'),
                            _divider(),
                            _bioRow(Icons.restaurant_outlined, 'Préférences',
                                prefs),
                            _divider(),
                            _bioRow(Icons.warning_amber_outlined, 'Allergies',
                                allergies),
                          ],
                        ),
                      ),
                      const SizedBox(height: 28),

                      // ── Confidentialité ─────────────────────────────
                      const Padding(
                        padding: EdgeInsets.only(left: 4, bottom: 12),
                        child: Text('CONFIDENTIALITÉ & DONNÉES',
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFFAAAAAA),
                                letterSpacing: 1.5)),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: const Color(0xFFEEEEEE), width: 1),
                        ),
                        child: Column(
                          children: [
                            _toggleRow(
                              'Partager avec mon médecin',
                              'Accès sécurisé pour Dr. Sylia',
                              _shareWithDoctor,
                              (v) {
                                setState(() => _shareWithDoctor = v);
                                _showSaveFeedback();
                              },
                            ),
                            _divider(),
                            _toggleRow(
                              'Participation à la recherche UCAD',
                              'Données anonymisées pour l\'Université',
                              _participateInResearch,
                              (v) {
                                setState(() => _participateInResearch = v);
                                _showSaveFeedback();
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 28),

                      // ── Settings ─────────────────────────────────────
                      const Padding(
                        padding: EdgeInsets.only(left: 4, bottom: 12),
                        child: Text('PARAMÈTRES',
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFFAAAAAA),
                                letterSpacing: 1.5)),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: const Color(0xFFEEEEEE), width: 1),
                        ),
                        child: Column(
                          children: [
                            _settingsRow(
                                Icons.notifications_outlined, 'Notifications'),
                            _divider(),
                            _settingsRow(Icons.language_outlined,
                                'Langue (Français / Wolof)'),
                            _divider(),
                            _settingsRow(
                                Icons.help_outline, 'Support & Contact'),
                            _divider(),
                            _settingsRow(Icons.star_border, 'Évaluer BiomeX'),
                            _divider(),
                            _settingsRow(Icons.description_outlined,
                                'Conditions d\'utilisation'),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // ── Logout ────────────────────────────────────────
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          onPressed: () => _confirmLogout(auth),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(
                                color: Color(0xFFFFCDD2), width: 1),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            backgroundColor: const Color(0xFFFFF5F5),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14)),
                          ),
                          child: const Text('Se déconnecter',
                              style: TextStyle(
                                  color: Color(0xFFE53935),
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600)),
                        ),
                      ),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Avatar widget ──────────────────────────────────────────────────────────
  Widget _buildAvatar(Map<String, dynamic>? user) {
    return Stack(
      children: [
        Container(
          width: 96,
          height: 96,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: const Color(0xFFF2E8D9),
            border: Border.all(color: const Color(0xFFE8D9C5), width: 2),
          ),
          child: user?['avatar'] != null
              ? ClipOval(
                  child: Image.network(user!['avatar'], fit: BoxFit.cover))
              : const Icon(Icons.person, size: 52, color: Color(0xFFA08060)),
        ),
        Positioned(
          bottom: 2,
          right: 2,
          child: GestureDetector(
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Modification de l\'avatar en cours...'),
                  duration: Duration(seconds: 2),
                  backgroundColor: Color(0xFF1A4D2E),
                ),
              );
            },
            child: Container(
              width: 28,
              height: 28,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0xFF1A4D2E),
              ),
              child: const Icon(Icons.edit, color: Colors.white, size: 14),
            ),
          ),
        ),
      ],
    );
  }

  // ── Biological profile row ─────────────────────────────────────────────────
  Widget _bioRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      child: Row(
        children: [
          Icon(icon, size: 18, color: const Color(0xFFAAAAAA)),
          const SizedBox(width: 14),
          Expanded(
            child: Text(label,
                style: const TextStyle(
                    fontSize: 15,
                    color: Color(0xFF555555),
                    fontWeight: FontWeight.w400)),
          ),
          Text(value,
              style: const TextStyle(
                  fontSize: 15,
                  color: Color(0xFF1A1A2E),
                  fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  // ── Toggle row ────────────────────────────────────────────────────────────
  Widget _toggleRow(
      String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF1A1A2E))),
                const SizedBox(height: 3),
                Text(subtitle,
                    style: const TextStyle(
                        fontSize: 12, color: Color(0xFFAAAAAA))),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.white,
            activeTrackColor: const Color(0xFF1A4D2E),
            inactiveTrackColor: const Color(0xFFDDDDDD),
            inactiveThumbColor: Colors.white,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ],
      ),
    );
  }

  // ── Settings row ─────────────────────────────────────────────────────────
  Widget _settingsRow(IconData icon, String label) {
    return InkWell(
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$label - Fonctionnalité en développement'),
            duration: const Duration(seconds: 2),
            backgroundColor: const Color(0xFF1A4D2E),
          ),
        );
      },
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        child: Row(
          children: [
            Icon(icon, size: 18, color: const Color(0xFFAAAAAA)),
            const SizedBox(width: 14),
            Expanded(
                child: Text(label,
                    style: const TextStyle(
                        fontSize: 15,
                        color: Color(0xFF555555),
                        fontWeight: FontWeight.w400))),
            const Icon(Icons.chevron_right, size: 18, color: Color(0xFFCCCCCC)),
          ],
        ),
      ),
    );
  }

  // ── Divider ──────────────────────────────────────────────────────────────
  Widget _divider() =>
      const Divider(indent: 50, height: 1, color: Color(0xFFF0F0F0));

  void _showSaveFeedback() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Préférences mises à jour avec succès.'),
        duration: Duration(seconds: 2),
        backgroundColor: Color(0xFF1A4D2E),
      ),
    );
  }

  // ── Logout confirm ────────────────────────────────────────────────────────
  Future<void> _confirmLogout(AuthProvider auth) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Déconnexion'),
        content: const Text('Êtes-vous sûr de vouloir vous déconnecter ?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Annuler')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Déconnecter',
                style: TextStyle(color: Color(0xFFE53935))),
          ),
        ],
      ),
    );
    if (confirm == true && mounted) {
      await auth.logout();
    }
  }
}
