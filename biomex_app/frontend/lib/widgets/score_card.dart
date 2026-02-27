import 'package:flutter/material.dart';
import '../constants/app_theme.dart';

class ScoreCard extends StatelessWidget {
  final int score;
  final String status;
  final int speciesCount;
  final int probioticCount;
  final double pathogenPercentage;
  final bool isLoading;

  const ScoreCard({
    super.key,
    required this.score,
    required this.status,
    required this.speciesCount,
    required this.probioticCount,
    required this.pathogenPercentage,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Container(
        height: 280,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: AppColors.primaryGradient,
          ),
          borderRadius: BorderRadius.circular(24),
        ),
        child: const Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }

    final hasData = score > 0;

    String statusText;
    Color statusColor;
    
    switch (status) {
      case 'excellent':
        statusText = 'EXCELLENT';
        statusColor = AppColors.success;
        break;
      case 'tres_bon':
        statusText = 'TRÈS BON';
        statusColor = AppColors.accent;
        break;
      case 'bon':
        statusText = 'BON';
        statusColor = AppColors.info;
        break;
      case 'a_ameliorer':
        statusText = 'À AMÉLIORER';
        statusColor = AppColors.warning;
        break;
      default:
        statusText = 'PAS DE DONNÉES';
        statusColor = Colors.white70;
    }

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: AppColors.primaryGradient,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Votre score microbiome',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white70,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Score Circle
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 140,
                height: 140,
                child: CircularProgressIndicator(
                  value: hasData ? score / 100 : 0,
                  strokeWidth: 12,
                  backgroundColor: Colors.white.withOpacity(0.2),
                  valueColor: AlwaysStoppedAnimation<Color>(
                    hasData ? AppColors.accent : Colors.white30,
                  ),
                ),
              ),
              Column(
                children: [
                  Text(
                    hasData ? '$score' : '-',
                    style: const TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const Text(
                    'sur 100',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Stats
          if (hasData)
            Text(
              'Basé sur $speciesCount espèces identifiées dans votre échantillon',
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white70,
              ),
              textAlign: TextAlign.center,
            )
          else
            const Text(
              'Commandez votre kit BiomeX pour découvrir votre score',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white70,
              ),
              textAlign: TextAlign.center,
            ),
          
          const SizedBox(height: 20),
          
          // Bottom stats
          if (hasData)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _StatItem(
                  label: 'ESPÈCES',
                  value: '$speciesCount',
                ),
                Container(
                  width: 1,
                  height: 30,
                  color: Colors.white.withOpacity(0.3),
                ),
                _StatItem(
                  label: 'PROBIOTIQUES',
                  value: '$probioticCount',
                ),
                Container(
                  width: 1,
                  height: 30,
                  color: Colors.white.withOpacity(0.3),
                ),
                _StatItem(
                  label: 'PATHOGÈNES',
                  value: '${pathogenPercentage.toStringAsFixed(0)}%',
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;

  const _StatItem({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Colors.white.withOpacity(0.7),
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }
}
