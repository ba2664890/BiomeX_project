import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

import '../../constants/app_theme.dart';
import '../../services/recommendation_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen>
    with SingleTickerProviderStateMixin {
  final RecommendationService _recommendationService = RecommendationService();
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FlutterTts _tts = FlutterTts();
  final stt.SpeechToText _speechToText = stt.SpeechToText();

  static const String _historyStorageKey = 'biomex_chat_history_v2';
  static const String _welcomeMessage = 'Bonjour, je suis l’assistant BiomeX.\n'
      'Pose ta question et je te réponds avec des recommandations nutritionnelles adaptées.';

  final List<_ChatMessage> _messages = <_ChatMessage>[
    _ChatMessage(
      role: _ChatRole.assistant,
      text: _welcomeMessage,
    ),
  ];

  static const List<String> _quickPrompts = [
    'Quels aliments réduire pour limiter l’inflammation ?',
    'Propose un plan repas simple sur 3 jours.',
    'Quels probiotiques naturels pour améliorer ma digestion ?',
  ];

  late final AnimationController _pulseController;
  bool _isSending = false;
  bool _isSpeaking = false;
  bool _isListening = false;
  bool _speechAvailable = false;
  bool _historyLoaded = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
    _restoreHistory();
    _configureAudio();
  }

  @override
  void dispose() {
    _tts.stop();
    _speechToText.stop();
    _pulseController.dispose();
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _configureAudio() async {
    try {
      await _tts.awaitSpeakCompletion(true);
      await _tts.setLanguage('fr-FR');
      await _tts.setSpeechRate(0.44);
      await _tts.setPitch(1.0);
    } catch (_) {
      // Keep silent fallback if TTS is unavailable on platform.
    }

    _tts.setStartHandler(() {
      if (!mounted) return;
      setState(() => _isSpeaking = true);
    });
    _tts.setCompletionHandler(() {
      if (!mounted) return;
      setState(() => _isSpeaking = false);
    });
    _tts.setCancelHandler(() {
      if (!mounted) return;
      setState(() => _isSpeaking = false);
    });
    _tts.setErrorHandler((_) {
      if (!mounted) return;
      setState(() => _isSpeaking = false);
      _showSnack('Audio indisponible sur cet appareil.');
    });

    try {
      final initialized = await _speechToText.initialize(
        onStatus: (status) {
          if (!mounted) return;
          if (status == 'notListening' || status == 'done') {
            setState(() => _isListening = false);
            // Auto-send if we stopped naturally and have content
            if (_inputController.text.trim().isNotEmpty) {
               _sendMessage();
            }
          }
        },
        onError: (error) {
          if (!mounted) return;
          setState(() => _isListening = false);
          _showSnack('Dictée vocale indisponible: ${error.errorMsg}');
        },
      );
      if (mounted) {
        setState(() => _speechAvailable = initialized);
      }
    } catch (_) {
      if (mounted) {
        setState(() => _speechAvailable = false);
      }
    }
  }

  Future<void> _restoreHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_historyStorageKey);
      if (raw == null || raw.trim().isEmpty) {
        if (mounted) setState(() => _historyLoaded = true);
        return;
      }

      final decoded = jsonDecode(raw);
      if (decoded is! List) {
        if (mounted) setState(() => _historyLoaded = true);
        return;
      }

      final restored = <_ChatMessage>[];
      for (final item in decoded) {
        if (item is Map<String, dynamic>) {
          restored.add(_ChatMessage.fromJson(item));
        } else if (item is Map) {
          restored.add(_ChatMessage.fromJson(Map<String, dynamic>.from(item)));
        }
      }

      if (restored.isNotEmpty && mounted) {
        setState(() {
          _messages
            ..clear()
            ..addAll(restored);
        });
        _scrollToBottom();
      }
    } catch (_) {
      // History restore should not break the chat.
    } finally {
      if (mounted) {
        setState(() => _historyLoaded = true);
      }
    }
  }

  Future<void> _persistHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final trimmed = _messages.length > 140
          ? _messages.sublist(_messages.length - 140)
          : List<_ChatMessage>.from(_messages);
      final raw =
          jsonEncode(trimmed.map((message) => message.toJson()).toList());
      await prefs.setString(_historyStorageKey, raw);
    } catch (_) {
      // Persist failures should not block interaction.
    }
  }

  Future<void> _sendMessage([String? presetMessage]) async {
    final question = (presetMessage ?? _inputController.text).trim();
    if (question.isEmpty || _isSending) return;

    if (_isListening) {
      await _speechToText.stop();
      if (mounted) setState(() => _isListening = false);
    }

    if (_isSpeaking) {
      await _tts.stop();
      if (mounted) setState(() => _isSpeaking = false);
    }

    setState(() {
      _isSending = true;
      _messages.add(_ChatMessage(role: _ChatRole.user, text: question));
    });
    _inputController.clear();
    _scrollToBottom();
    await _persistHistory();

    try {
      final response =
          await _recommendationService.askRagChatbot(question: question);
      final answer = (response['answer'] ?? '').toString().trim();
      final degraded = response['degraded'] == true;
      final sourcesRaw = response['sources'];
      final List<String> sources = [];

      if (sourcesRaw is List) {
        for (final source in sourcesRaw) {
          if (source is Map) {
            final name = source['name']?.toString() ?? '';
            final sourceType = source['source_type']?.toString() ?? '';
            final score = source['score']?.toString() ?? '';
            final label = [
              name,
              sourceType,
              score.isNotEmpty ? 'score=$score' : '',
            ].where((v) => v.isNotEmpty).join(' • ');
            if (label.isNotEmpty) {
              sources.add(label);
            }
          }
        }
      }

      if (!mounted) return;
      setState(() {
        _messages.add(
          _ChatMessage(
            role: _ChatRole.assistant,
            text: answer.isEmpty ? 'Aucune réponse générée.' : answer,
            sources: sources,
            degraded: degraded,
          ),
        );
      });
      await _persistHistory();
      
      // Auto-speak the response
      if (answer.isNotEmpty) {
        await _speakText(answer);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.add(
          _ChatMessage(
            role: _ChatRole.assistant,
            text: 'Erreur: ${e.toString().replaceFirst('Exception: ', '')}',
            degraded: true,
          ),
        );
      });
      await _persistHistory();
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
        _scrollToBottom();
      }
    }
  }

  Future<void> _toggleListening() async {
    if (!_speechAvailable) {
      _showSnack('Dictée vocale non disponible sur cet appareil.');
      return;
    }

    if (_isListening) {
      await _speechToText.stop();
      if (mounted) {
        setState(() => _isListening = false);
      }
      // If there is text in the controller, auto-send it
      if (_inputController.text.trim().isNotEmpty) {
        _sendMessage();
      }
      return;
    }

    // Stop bot speaking before listening
    if (_isSpeaking) {
      await _tts.stop();
      if (mounted) setState(() => _isSpeaking = false);
    }

    try {
      await _speechToText.listen(
        localeId: 'fr_FR',
        listenOptions: stt.SpeechListenOptions(
          cancelOnError: true,
          partialResults: true,
          listenMode: stt.ListenMode.confirmation, // Better for short commands/questions
        ),
        onResult: (result) {
          final text = result.recognizedWords;
          _inputController.value = TextEditingValue(
            text: text,
            selection: TextSelection.collapsed(offset: text.length),
          );
        },
      );
      if (mounted) {
        setState(() => _isListening = true);
      }

      // Auto-stop listening and send after enough words or silence
      // Note: speech_to_text already handles silence detection based on its internal timer
    } catch (_) {
      _showSnack('Impossible de démarrer la dictée vocale.');
    }
  }

  Future<void> _speakText(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return;

    try {
      await _tts.stop();
      await _tts.speak(trimmed);
    } catch (_) {
      _showSnack('Lecture audio indisponible.');
    }
  }

  Future<void> _stopSpeaking() async {
    try {
      await _tts.stop();
    } catch (_) {}
    if (!mounted) return;
    setState(() => _isSpeaking = false);
  }

  Future<void> _copyText(String value, {String message = 'Texte copié'}) async {
    await Clipboard.setData(ClipboardData(text: value));
    _showSnack(message);
  }

  Future<void> _copyConversation() async {
    final transcript = _buildTranscript();
    if (transcript.trim().isEmpty) {
      _showSnack('Aucun message à copier.');
      return;
    }
    await _copyText(transcript, message: 'Conversation copiée');
  }

  String _buildTranscript() {
    final buffer = StringBuffer();
    for (final message in _messages) {
      final who = message.role == _ChatRole.user ? 'Vous' : 'BiomeX';
      final time = _MessageBubble.formatTime(message.createdAt);
      buffer.writeln('[$time] $who');
      buffer.writeln(message.text);
      if (message.sources.isNotEmpty) {
        buffer.writeln('Sources: ${message.sources.join(' | ')}');
      }
      buffer.writeln('');
    }
    return buffer.toString();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOutCubic,
      );
    });
  }

  Future<void> _clearConversation() async {
    setState(() {
      _messages
        ..clear()
        ..add(
          _ChatMessage(
            role: _ChatRole.assistant,
            text:
                'Conversation réinitialisée. Pose une nouvelle question sur ton microbiome ou ton alimentation.',
          ),
        );
    });
    await _persistHistory();
  }

  void _showHistorySheet() {
    final history = _messages.reversed.toList(growable: false);

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.62,
          minChildSize: 0.35,
          maxChildSize: 0.92,
          builder: (context, controller) {
            return Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
              ),
              child: Column(
                children: [
                  const SizedBox(height: 10),
                  Container(
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AppColors.textTertiary.withValues(alpha: 0.35),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
                    child: Row(
                      children: [
                        const Text(
                          'Historique',
                          style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${_messages.length} messages',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Divider(height: 1),
                  Expanded(
                    child: !_historyLoaded
                        ? const Center(child: CircularProgressIndicator())
                        : history.isEmpty
                            ? const Center(
                                child: Text(
                                  'Aucun historique disponible.',
                                  style:
                                      TextStyle(color: AppColors.textSecondary),
                                ),
                              )
                            : ListView.builder(
                                controller: controller,
                                itemCount: history.length,
                                itemBuilder: (context, index) {
                                  final message = history[index];
                                  final isUser = message.role == _ChatRole.user;
                                  return ListTile(
                                    dense: true,
                                    leading: CircleAvatar(
                                      radius: 14,
                                      backgroundColor: isUser
                                          ? AppColors.accent
                                              .withValues(alpha: 0.22)
                                          : AppColors.primary
                                              .withValues(alpha: 0.16),
                                      child: Icon(
                                        isUser
                                            ? Icons.person_rounded
                                            : Icons.auto_awesome_rounded,
                                        size: 14,
                                        color: isUser
                                            ? AppColors.primaryDark
                                            : AppColors.primary,
                                      ),
                                    ),
                                    title: Text(
                                      message.text.replaceAll('\n', ' '),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(fontSize: 13),
                                    ),
                                    subtitle: Text(
                                      _MessageBubble.formatTime(
                                          message.createdAt),
                                      style: const TextStyle(fontSize: 11),
                                    ),
                                    trailing: IconButton(
                                      icon: const Icon(
                                        Icons.content_copy_rounded,
                                        size: 18,
                                      ),
                                      onPressed: () => _copyText(
                                        message.text,
                                        message:
                                            'Message copié depuis l’historique',
                                      ),
                                    ),
                                    onTap: isUser
                                        ? () {
                                            _inputController.value =
                                                TextEditingValue(
                                              text: message.text,
                                              selection:
                                                  TextSelection.collapsed(
                                                offset: message.text.length,
                                              ),
                                            );
                                            Navigator.of(context).pop();
                                          }
                                        : null,
                                  );
                                },
                              ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _showSnack(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(text),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: const Text('Assistant BiomeX'),
        actions: [
          IconButton(
            tooltip: 'Historique',
            onPressed: _showHistorySheet,
            icon: const Icon(Icons.history_rounded),
          ),
          IconButton(
            tooltip: 'Copier conversation',
            onPressed: _copyConversation,
            icon: const Icon(Icons.content_copy_rounded),
          ),
          if (_isSpeaking)
            IconButton(
              tooltip: 'Arrêter audio',
              onPressed: _stopSpeaking,
              icon: const Icon(Icons.stop_circle_outlined),
            ),
          IconButton(
            tooltip: 'Réinitialiser',
            onPressed: _isSending ? null : _clearConversation,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.primaryLight.withValues(alpha: 0.09),
              AppColors.background,
              Colors.white,
            ],
          ),
        ),
        child: Column(
          children: [
            _buildHeaderCard(),
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.fromLTRB(14, 10, 14, 8),
                itemCount: _messages.length + (_isSending ? 1 : 0),
                itemBuilder: (context, index) {
                  if (_isSending && index == _messages.length) {
                    return _TypingBubble(animation: _pulseController);
                  }
                  final message = _messages[index];
                  return _MessageBubble(
                    message: message,
                    onCopy: () =>
                        _copyText(message.text, message: 'Message copié'),
                    onSpeak: message.role == _ChatRole.assistant
                        ? () => _speakText(message.text)
                        : null,
                  );
                },
              ),
            ),
            _buildQuickPrompts(),
            _buildInputBar(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 10, 14, 8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: const LinearGradient(
            colors: [Color(0xFF1A4D2E), Color(0xFF2C7A44)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.primaryDark.withValues(alpha: 0.25),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 34,
                  height: 34,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.auto_awesome_rounded,
                    color: Color(0xFFFFD54F),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    'Réponses contextualisées avec tes données BiomeX',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                      height: 1.25,
                    ),
                  ),
                ),
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (_, __) {
                    final scale = 0.85 +
                        (math.sin(_pulseController.value * 2 * math.pi) + 1) *
                            0.1;
                    return Transform.scale(
                      scale: scale,
                      child: Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          color: Color(0xFF7CFF9A),
                          shape: BoxShape.circle,
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _statusPill(
                  icon: Icons.history_rounded,
                  label: '${_messages.length} msgs',
                ),
                _statusPill(
                  icon: Icons.volume_up_rounded,
                  label: _isSpeaking ? 'Lecture audio' : 'Audio prêt',
                ),
                _statusPill(
                  icon:
                      _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                  label: _speechAvailable
                      ? (_isListening ? 'Dictée active' : 'Dictée dispo')
                      : 'Dictée indispo',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusPill({required IconData icon, required String label}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.28)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickPrompts() {
    return SizedBox(
      height: 46,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        itemCount: _quickPrompts.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final prompt = _quickPrompts[index];
          return ActionChip(
            avatar: const Icon(Icons.bolt_rounded, size: 15),
            label: Text(
              prompt,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            onPressed: _isSending ? null : () => _sendMessage(prompt),
            backgroundColor: Colors.white,
            side: BorderSide(color: AppColors.primary.withValues(alpha: 0.18)),
          );
        },
      ),
    );
  }

  Widget _buildInputBar() {
    return SafeArea(
      top: false,
      child: Container(
        margin: const EdgeInsets.fromLTRB(12, 8, 12, 10),
        padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 14,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _inputController,
                maxLines: 4,
                minLines: 1,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _sendMessage(),
                decoration: InputDecoration(
                  hintText: _isListening
                      ? 'Je t’écoute... parle maintenant'
                      : 'Ex: Quels aliments privilégier cette semaine ?',
                  border: InputBorder.none,
                  focusedBorder: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  filled: false,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 8),
                ),
              ),
            ),
            const SizedBox(width: 8),
            AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: _isListening
                    ? AppColors.warning
                    : AppColors.primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: IconButton(
                tooltip: 'Dictée vocale',
                onPressed: _isSending ? null : _toggleListening,
                icon: Icon(
                  _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                  color: _isListening ? Colors.white : AppColors.primary,
                ),
              ),
            ),
            const SizedBox(width: 8),
            AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: _isSending ? AppColors.primaryLight : AppColors.primary,
                borderRadius: BorderRadius.circular(12),
              ),
              child: IconButton(
                onPressed: _isSending ? null : () => _sendMessage(),
                icon: _isSending
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.send_rounded, color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  const _TypingBubble({required this.animation});

  final Animation<double> animation;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.smart_toy_outlined,
              size: 16,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFEAEAEA)),
            ),
            child: AnimatedBuilder(
              animation: animation,
              builder: (_, __) {
                final t = animation.value * 2 * math.pi;
                return Row(
                  mainAxisSize: MainAxisSize.min,
                  children: List.generate(3, (index) {
                    final wave = (math.sin(t - (index * 0.9)) + 1) / 2;
                    final size = 6 + wave * 2.4;
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2),
                      child: Container(
                        width: size,
                        height: size,
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(
                            alpha: 0.35 + wave * 0.55,
                          ),
                          shape: BoxShape.circle,
                        ),
                      ),
                    );
                  }),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({
    required this.message,
    this.onCopy,
    this.onSpeak,
  });

  final _ChatMessage message;
  final VoidCallback? onCopy;
  final VoidCallback? onSpeak;

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == _ChatRole.user;
    final maxBubbleWidth = MediaQuery.of(context).size.width * 0.78;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.auto_awesome_rounded,
                color: AppColors.primary,
                size: 16,
              ),
            ),
            const SizedBox(width: 8),
          ],
          GestureDetector(
            onLongPress: onCopy,
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: maxBubbleWidth),
              child: Container(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
                decoration: BoxDecoration(
                  gradient: isUser
                      ? const LinearGradient(
                          colors: [Color(0xFF1A4D2E), Color(0xFF2C7A44)],
                        )
                      : null,
                  color: isUser ? null : Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: isUser
                      ? null
                      : Border.all(color: const Color(0xFFEAEAEA)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.04),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: isUser
                      ? CrossAxisAlignment.end
                      : CrossAxisAlignment.start,
                  children: [
                    _MessageBody(message: message),
                    if (message.degraded && !isUser) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 5,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.warning.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'Mode dégradé',
                          style: TextStyle(
                            color: AppColors.warning,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                    if (message.sources.isNotEmpty && !isUser) ...[
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: message.sources.take(4).map((source) {
                          return Container(
                            constraints: const BoxConstraints(maxWidth: 220),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withValues(alpha: 0.08),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              source,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                    const SizedBox(height: 6),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (onCopy != null) ...[
                          _tinyAction(
                            icon: Icons.content_copy_rounded,
                            color: isUser
                                ? Colors.white.withValues(alpha: 0.85)
                                : AppColors.textSecondary,
                            onTap: onCopy!,
                          ),
                          const SizedBox(width: 6),
                        ],
                        if (onSpeak != null) ...[
                          _tinyAction(
                            icon: Icons.volume_up_rounded,
                            color: AppColors.textSecondary,
                            onTap: onSpeak!,
                          ),
                          const SizedBox(width: 6),
                        ],
                        Text(
                          formatTime(message.createdAt),
                          style: TextStyle(
                            fontSize: 10,
                            color: isUser
                                ? Colors.white.withValues(alpha: 0.75)
                                : AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: AppColors.accent.withValues(alpha: 0.24),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.person_rounded,
                color: AppColors.primaryDark,
                size: 16,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _tinyAction({
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.all(2),
        child: Icon(icon, size: 14, color: color),
      ),
    );
  }

  static String formatTime(DateTime time) {
    final h = time.hour.toString().padLeft(2, '0');
    final m = time.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }
}

class _MessageBody extends StatelessWidget {
  const _MessageBody({required this.message});

  final _ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == _ChatRole.user;
    final baseStyle = TextStyle(
      color: isUser ? Colors.white : AppColors.textPrimary,
      fontSize: 14,
      height: 1.35,
    );

    if (isUser) {
      return Text(message.text, style: baseStyle);
    }

    final lines = message.text.split('\n');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: lines.map((line) {
        final trimmed = line.trimRight();
        if (trimmed.isEmpty) {
          return const SizedBox(height: 7);
        }
        final isSectionTitle = RegExp(r'^\d\)').hasMatch(trimmed);
        final isBullet = trimmed.startsWith('- ');
        if (isSectionTitle) {
          return Padding(
            padding: const EdgeInsets.only(top: 4, bottom: 2),
            child: Text(
              trimmed,
              style: baseStyle.copyWith(
                fontWeight: FontWeight.w700,
                color: AppColors.primaryDark,
              ),
            ),
          );
        }
        if (isBullet) {
          return Padding(
            padding: const EdgeInsets.only(left: 2, bottom: 2),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: 7),
                  child: Icon(
                    Icons.circle,
                    size: 5,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    trimmed.substring(2),
                    style: baseStyle,
                  ),
                ),
              ],
            ),
          );
        }
        return Text(trimmed, style: baseStyle);
      }).toList(),
    );
  }
}

enum _ChatRole { user, assistant }

class _ChatMessage {
  _ChatMessage({
    required this.role,
    required this.text,
    this.sources = const [],
    this.degraded = false,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory _ChatMessage.fromJson(Map<String, dynamic> json) {
    final roleValue = (json['role'] ?? 'assistant').toString();
    final role = roleValue == 'user' ? _ChatRole.user : _ChatRole.assistant;
    final text = (json['text'] ?? '').toString();
    final sources = (json['sources'] is List)
        ? (json['sources'] as List).map((e) => e.toString()).toList()
        : const <String>[];
    final degraded = json['degraded'] == true;
    final createdAt = DateTime.tryParse(
          (json['created_at'] ?? '').toString(),
        ) ??
        DateTime.now();

    return _ChatMessage(
      role: role,
      text: text,
      sources: sources,
      degraded: degraded,
      createdAt: createdAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'role': role.name,
      'text': text,
      'sources': sources,
      'degraded': degraded,
      'created_at': createdAt.toIso8601String(),
    };
  }

  final _ChatRole role;
  final String text;
  final List<String> sources;
  final bool degraded;
  final DateTime createdAt;
}
