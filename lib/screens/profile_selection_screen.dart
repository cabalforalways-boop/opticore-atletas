import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../data/profile_templates.dart';
import '../services/api_service.dart';

class ProfileSelectionScreen extends StatefulWidget {
  const ProfileSelectionScreen({super.key});

  @override
  State<ProfileSelectionScreen> createState() => _ProfileSelectionScreenState();
}

class _ProfileSelectionScreenState extends State<ProfileSelectionScreen> {
  bool? _serverOnline;

  @override
  void initState() {
    super.initState();
    _checkServer();
  }

  Future<void> _checkServer() async {
    final ok = await ApiService.checkHealth();
    if (mounted) setState(() => _serverOnline = ok);
  }

  @override
  Widget build(BuildContext context) {
    final profiles = ProfileTemplates.getAll();

    return Scaffold(
      // FIX: emoji correcto en AppBar
      appBar: AppBar(
        title: const Text('🏋️ OptiCore Atletas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Historial',
            onPressed: () => context.push('/history'),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Configuración',
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          // Indicador de estado del servidor
          _ServerStatusBanner(online: _serverOnline, onRetry: _checkServer),

          // Cabecera
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Selecciona tu objetivo deportivo',
                  style: Theme.of(context)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Optimización LP basada en ISSN 2017 · ACSM 2016 · USDA FoodData Central',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: Colors.grey.shade600),
                ),
              ],
            ),
          ),

          // Grid de perfiles
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 0.88,
                ),
                itemCount: profiles.length,
                itemBuilder: (ctx, i) {
                  final p = profiles[i];
                  return _ProfileCard(
                    profile: p,
                    onTap: () => context.push('/diet/${p.id}'),
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}

// ── Tarjeta de perfil ─────────────────────────────────────────────────────────
class _ProfileCard extends StatelessWidget {
  final dynamic profile;
  final VoidCallback onTap;

  const _ProfileCard({required this.profile, required this.onTap});

  static const _gradients = [
    [Color(0xFF1565C0), Color(0xFF42A5F5)], // azul — fuerza
    [Color(0xFF2E7D32), Color(0xFF66BB6A)], // verde — resistencia
    [Color(0xFFBF360C), Color(0xFFFF7043)], // naranja — definición
    [Color(0xFF6A1B9A), Color(0xFFBA68C8)], // morado — recuperación
  ];

  static const _icons = [
    Icons.fitness_center,
    Icons.directions_run,
    Icons.local_fire_department,
    Icons.bolt,
  ];

  @override
  Widget build(BuildContext context) {
    final idx = ProfileTemplates.getAll().indexOf(profile);
    final grad = _gradients[idx % _gradients.length];
    final icon = _icons[idx % _icons.length];

    // Nombre limpio sin paréntesis
    final shortName = profile.name
        .replaceAll(RegExp(r'\s*\(.*?\)'), '')
        .replaceAll(RegExp(r'^[^\w\s]+\s*'), ''); // quitar emoji del nombre

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: grad,
            ),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(profile.emoji, style: const TextStyle(fontSize: 44)),
              const SizedBox(height: 8),
              Text(
                shortName,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Icon(icon, color: Colors.white60, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Banner de estado del servidor ─────────────────────────────────────────────
class _ServerStatusBanner extends StatelessWidget {
  final bool? online;
  final VoidCallback onRetry;

  const _ServerStatusBanner({required this.online, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    if (online == null) {
      return const LinearProgressIndicator(minHeight: 2);
    }
    if (online == true) return const SizedBox.shrink();

    return MaterialBanner(
      backgroundColor: Colors.red.shade50,
      leading: const Icon(Icons.wifi_off, color: Colors.red),
      content: Text(
        'Servidor no disponible en ${ApiService.baseUrl}. '
        'Configura la IP en Ajustes.',
        style: const TextStyle(fontSize: 12),
      ),
      actions: [
        TextButton(onPressed: onRetry, child: const Text('Reintentar')),
        TextButton(
          onPressed: () => context.push('/settings'),
          child: const Text('Ajustes'),
        ),
      ],
    );
  }
}
