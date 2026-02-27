import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../constants/app_theme.dart';

class MediaReelSection extends StatefulWidget {
  const MediaReelSection({super.key});

  @override
  State<MediaReelSection> createState() => _MediaReelSectionState();
}

class _MediaReelSectionState extends State<MediaReelSection> {
  static const _items = <Map<String, dynamic>>[
    {
      'title': 'Microbiome Food Lab',
      'subtitle': 'Images cliniques des aliments bénéfiques',
      'tag': 'IMAGE',
      'image':
          'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1100&q=80',
      'isVideo': false,
    },
    {
      'title': 'Capsule digestion',
      'subtitle': 'Mini vidéo explicative sur l’axe intestin-cerveau',
      'tag': 'VIDEO',
      'image':
          'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWRvN2NsZWY3emhmb3l2cHlrNGRwd2JhamxweTdwcTUxZG5lYzA1cyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/26BRuo6sLetdllPAQ/giphy.gif',
      'isVideo': true,
    },
    {
      'title': 'Nutriments locaux',
      'subtitle': 'Sélection visuelle de super-aliments africains',
      'tag': 'IMAGE',
      'image':
          'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=1100&q=80',
      'isVideo': false,
    },
  ];

  final PageController _pageController = PageController(viewportFraction: 0.88);
  int _currentPage = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Media Lab',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'Images et capsules visuelles pour dynamiser le suivi',
          style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
        ),
        const SizedBox(height: 14),
        SizedBox(
          height: 188,
          child: PageView.builder(
            controller: _pageController,
            itemCount: _items.length,
            onPageChanged: (index) => setState(() => _currentPage = index),
            itemBuilder: (context, index) {
              final item = _items[index];
              final isVideo = item['isVideo'] == true;
              return Padding(
                padding:
                    EdgeInsets.only(right: index == _items.length - 1 ? 0 : 10),
                child: _MediaCard(
                  title: item['title'] as String,
                  subtitle: item['subtitle'] as String,
                  tag: item['tag'] as String,
                  imageUrl: item['image'] as String,
                  isVideo: isVideo,
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: List.generate(_items.length, (index) {
            final active = index == _currentPage;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 220),
              margin: const EdgeInsets.only(right: 6),
              width: active ? 20 : 7,
              height: 7,
              decoration: BoxDecoration(
                color: active
                    ? AppColors.primary
                    : AppColors.textTertiary.withValues(alpha: 0.35),
                borderRadius: BorderRadius.circular(8),
              ),
            );
          }),
        ),
      ],
    );
  }
}

class _MediaCard extends StatelessWidget {
  const _MediaCard({
    required this.title,
    required this.subtitle,
    required this.tag,
    required this.imageUrl,
    required this.isVideo,
  });

  final String title;
  final String subtitle;
  final String tag;
  final String imageUrl;
  final bool isVideo;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.11),
            blurRadius: 14,
            offset: const Offset(0, 7),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(18),
        child: Stack(
          fit: StackFit.expand,
          children: [
            CachedNetworkImage(
              imageUrl: imageUrl,
              fit: BoxFit.cover,
              placeholder: (_, __) => Container(color: const Color(0xFFE8ECEF)),
              errorWidget: (_, __, ___) => Container(
                color: const Color(0xFF1A4D2E),
                child: const Icon(Icons.broken_image, color: Colors.white),
              ),
            ),
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.15),
                    Colors.black.withValues(alpha: 0.68),
                  ],
                ),
              ),
            ),
            if (isVideo)
              Center(
                child: Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withValues(alpha: 0.24),
                    border:
                        Border.all(color: Colors.white.withValues(alpha: 0.5)),
                  ),
                  child: const Icon(
                    Icons.play_arrow_rounded,
                    color: Colors.white,
                    size: 32,
                  ),
                ),
              ),
            Positioned(
              top: 10,
              left: 10,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border:
                      Border.all(color: Colors.white.withValues(alpha: 0.38)),
                ),
                child: Text(
                  tag,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                  ),
                ),
              ),
            ),
            Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.9),
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      height: 1.25,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
