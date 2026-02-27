import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../constants/app_theme.dart';

class AnimatedStage extends StatefulWidget {
  const AnimatedStage({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  State<AnimatedStage> createState() => _AnimatedStageState();
}

class _AnimatedStageState extends State<AnimatedStage>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 14),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final t = _controller.value * 2 * math.pi;

        return Stack(
          children: [
            Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xFFF4FBF5),
                    Color(0xFFF8F9FA),
                    Color(0xFFFFFFFF),
                  ],
                ),
              ),
            ),
            Positioned(
              top: -48 + math.sin(t) * 18,
              right: -36,
              child: _glowOrb(
                size: 170,
                color: AppColors.primaryLight.withValues(alpha: 0.17),
              ),
            ),
            Positioned(
              left: -64,
              top: 220 + math.cos(t * 0.8) * 24,
              child: _glowOrb(
                size: 210,
                color: AppColors.accent.withValues(alpha: 0.11),
              ),
            ),
            Positioned(
              right: 16 + math.sin(t * 1.3) * 20,
              bottom: 48,
              child: _glowOrb(
                size: 130,
                color: AppColors.primary.withValues(alpha: 0.1),
              ),
            ),
            widget.child,
          ],
        );
      },
    );
  }

  Widget _glowOrb({required double size, required Color color}) {
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
          boxShadow: [
            BoxShadow(
              color: color,
              blurRadius: 42,
              spreadRadius: 6,
            ),
          ],
        ),
      ),
    );
  }
}
