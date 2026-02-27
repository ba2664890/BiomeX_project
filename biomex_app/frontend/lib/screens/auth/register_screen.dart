import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../constants/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/custom_text_field.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _agreeToTerms = false;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (_formKey.currentState?.validate() ?? false) {
      if (!_agreeToTerms) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Veuillez accepter les conditions d\'utilisation'),
            backgroundColor: AppColors.error,
          ),
        );
        return;
      }

      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      
      final success = await authProvider.register(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        passwordConfirm: _confirmPasswordController.text,
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        phone: _phoneController.text.trim().isEmpty
            ? null
            : _phoneController.text.trim(),
      );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Compte créé avec succès ! Veuillez vous connecter.'),
            backgroundColor: AppColors.success,
          ),
        );
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.primaryDark,
              AppColors.primary.withOpacity(0.9),
              AppColors.primaryLight.withOpacity(0.1),
            ],
            stops: const [0.0, 0.4, 1.0],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Back Button Row
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    const Text(
                      'Retour',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                  child: Column(
                    children: [
                      // Header Section
                      const Icon(Icons.person_add_rounded, size: 48, color: Colors.white),
                      const SizedBox(height: 16),
                      const Text(
                        'Créer un compte',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.w900,
                          color: Colors.white,
                          letterSpacing: -0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Rejoignez l\'aventure BiomeX',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.white.withOpacity(0.85),
                        ),
                      ),
                      const SizedBox(height: 32),
                      
                      // Form Card
                      Container(
                        padding: const EdgeInsets.all(28),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.95),
                          borderRadius: BorderRadius.circular(32),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 30,
                              offset: const Offset(0, 15),
                            ),
                          ],
                        ),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (authProvider.error != null) ...[
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                  decoration: BoxDecoration(
                                    color: AppColors.error.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: AppColors.error.withOpacity(0.2)),
                                  ),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.error_outline_rounded, color: AppColors.error, size: 20),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Text(
                                          authProvider.error!,
                                          style: const TextStyle(color: AppColors.error, fontSize: 13, fontWeight: FontWeight.w600),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 20),
                              ],
                              
                              // Identity Section
                              Row(
                                children: [
                                  Expanded(
                                    child: CustomTextField(
                                      controller: _firstNameController,
                                      label: 'Prénom',
                                      hint: 'Jean',
                                      prefixIcon: Icons.person_outline_rounded,
                                      validator: (value) => (value == null || value.isEmpty) ? 'Requis' : null,
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: CustomTextField(
                                      controller: _lastNameController,
                                      label: 'Nom',
                                      hint: 'Dupont',
                                      prefixIcon: Icons.badge_outlined,
                                      validator: (value) => (value == null || value.isEmpty) ? 'Requis' : null,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 20),
                              CustomTextField(
                                controller: _emailController,
                                label: 'Email',
                                hint: 'votre@email.com',
                                keyboardType: TextInputType.emailAddress,
                                prefixIcon: Icons.alternate_email_rounded,
                                validator: (value) {
                                  if (value == null || value.isEmpty) return 'L\'email est requis';
                                  if (!value.contains('@')) return 'Email invalide';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 20),
                              CustomTextField(
                                controller: _phoneController,
                                label: 'Téléphone (optionnel)',
                                hint: '+221 77 123 45 67',
                                keyboardType: TextInputType.phone,
                                prefixIcon: Icons.phone_iphone_rounded,
                              ),
                              const SizedBox(height: 20),
                              CustomTextField(
                                controller: _passwordController,
                                label: 'Mot de passe',
                                hint: '••••••••',
                                obscureText: _obscurePassword,
                                prefixIcon: Icons.lock_outline_rounded,
                                suffixIcon: _obscurePassword ? Icons.visibility_rounded : Icons.visibility_off_rounded,
                                onSuffixIconPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                validator: (value) {
                                  if (value == null || value.isEmpty) return 'Requis';
                                  if (value.length < 6) return 'Mini 6 chars';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 20),
                              CustomTextField(
                                controller: _confirmPasswordController,
                                label: 'Confirmation',
                                hint: '••••••••',
                                obscureText: _obscureConfirmPassword,
                                prefixIcon: Icons.lock_outline,
                                suffixIcon: _obscureConfirmPassword ? Icons.visibility_rounded : Icons.visibility_off_rounded,
                                onSuffixIconPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                                validator: (value) {
                                  if (value != _passwordController.text) return 'Pas identique';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                              // Terms checkbox
                              Theme(
                                data: ThemeData(unselectedWidgetColor: AppColors.textTertiary),
                                child: CheckboxListTile(
                                  value: _agreeToTerms,
                                  onChanged: (value) => setState(() => _agreeToTerms = value ?? false),
                                  activeColor: AppColors.primary,
                                  contentPadding: EdgeInsets.zero,
                                  dense: true,
                                  controlAffinity: ListTileControlAffinity.leading,
                                  title: Text.rich(
                                    TextSpan(
                                      text: 'J\'accepte les ',
                                      style: TextStyle(color: AppColors.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
                                      children: [
                                        TextSpan(
                                          text: 'Conditions d\'utilisation',
                                          style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w800),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 24),
                              CustomButton(
                                text: 'CRÉER MON COMPTE',
                                onPressed: _register,
                                isLoading: authProvider.isLoading,
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
