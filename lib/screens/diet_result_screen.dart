import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:share_plus/share_plus.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/profile.dart';
import '../models/diet_history_entry.dart';
import '../services/api_service.dart';
import '../data/profile_templates.dart';

class DietResultScreen extends StatefulWidget {
  final String profileId;
  const DietResultScreen({super.key, required this.profileId});

  @override
  State<DietResultScreen> createState() => _DietResultScreenState();
}

class _DietResultScreenState extends State<DietResultScreen>
    with SingleTickerProviderStateMixin {
  bool _loading = false;
  String _error = '';
  DietResult? _result;
  AthleteProfile? _profile;
  late TabController _tabController;

  final _currency = NumberFormat.currency(symbol: '\$', decimalDigits: 2);

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _profile = ProfileTemplates.getAll().firstWhere(
      (p) => p.id == widget.profileId,
      orElse: () => ProfileTemplates.fuerzaVolumen,
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // ── Calcular dieta ──────────────────────────────────────────────────────────
  Future<void> _runOptimization() async {
    setState(() { _loading = true; _error = ''; _result = null; });
    try {
      final payload = Map<String, dynamic>.from(_profile!.payloadTemplate);
      payload['metadata'] = {
        ...Map<String, dynamic>.from(payload['metadata'] as Map),
        'date': DateTime.now().toIso8601String(),
      };
      final res = await ApiService.calculateDiet(payload);
      setState(() => _result = res);

      // Guardar en historial Hive
      if (res.status == 'optimal') {
        await _saveToHistory(res);
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _saveToHistory(DietResult res) async {
    final box = Hive.box<DietHistoryEntry>('diet_history');
    await box.add(DietHistoryEntry(
      profileId:    _profile!.id,
      profileName:  _profile!.name,
      date:         DateTime.now(),
      costUsdPerKg: res.objectiveValue,
      solution:     Map<String, double>.from(res.solution),
      kcalPerKg:    res.totals.kcal,
      protGPerKg:   res.totals.protG,
      choGPerKg:    res.totals.choG,
      grasaGPerKg:  res.totals.grasaG,
    ));
  }

  // ── Compartir resultado ─────────────────────────────────────────────────────
  Future<void> _shareResult() async {
    if (_result == null) return;
    final t = _result!.totals;
    final sb = StringBuffer();
    sb.writeln('🏋️ OptiCore Atletas — ${_profile!.name}');
    sb.writeln('📅 ${DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now())}');
    sb.writeln();
    sb.writeln('💰 Costo: ${_currency.format(_result!.objectiveValue)} USD/kg');
    sb.writeln('🔥 Kcal:  ${t.kcal.toStringAsFixed(0)} kcal/kg');
    sb.writeln('💪 Prot:  ${t.protG.toStringAsFixed(1)} g/kg');
    sb.writeln('⚡ CHO:   ${t.choG.toStringAsFixed(1)} g/kg');
    sb.writeln('🫒 Grasa: ${t.grasaG.toStringAsFixed(1)} g/kg');
    sb.writeln();
    sb.writeln('📋 Receta óptima (g por kg de dieta):');
    final sorted = _result!.solution.entries
        .where((e) => e.value > 0.001)
        .toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    for (final e in sorted) {
      final emoji = kAlimentoEmoji[e.key] ?? '🍽️';
      sb.writeln('  $emoji ${e.key.replaceAll('_', ' ')}: '
          '${(e.value * 1000).toStringAsFixed(1)} g');
    }
    sb.writeln();
    sb.writeln('Generado con OptiCore Atletas v1.0 (LP/MILP · HiGHS solver)');
    await Share.share(sb.toString(), subject: 'Dieta Óptima OptiCore');
  }

  // ── UI ──────────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_profile?.emoji ?? '' + ' ' + (_profile?.name ?? 'Dieta')),
        bottom: _result != null
            ? TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                labelColor: Colors.white,
                unselectedLabelColor: Colors.white60,
                tabs: const [
                  Tab(icon: Icon(Icons.restaurant_menu), text: 'Receta'),
                  Tab(icon: Icon(Icons.pie_chart),       text: 'Gráfico'),
                  Tab(icon: Icon(Icons.analytics),       text: 'Nutrición'),
                ],
              )
            : null,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error.isNotEmpty
              ? _ErrorView(error: _error, onRetry: _runOptimization)
              : _result == null
                  ? _ProfileInfoView(
                      profile: _profile!,
                      onCalculate: _runOptimization,
                    )
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        _RecipeTab(result: _result!, currency: _currency),
                        _ChartTab(result: _result!),
                        _NutritionTab(result: _result!, currency: _currency),
                      ],
                    ),
      floatingActionButton: _result == null && !_loading && _error.isEmpty
          ? FloatingActionButton.extended(
              onPressed: _runOptimization,
              icon: const Icon(Icons.calculate),
              label: const Text('Calcular Dieta'),
              backgroundColor: const Color(0xFF1565C0),
              foregroundColor: Colors.white,
            )
          : _result != null
              ? FloatingActionButton.extended(
                  onPressed: _shareResult,
                  icon: const Icon(Icons.share),
                  label: const Text('Compartir'),
                  backgroundColor: Colors.green.shade700,
                  foregroundColor: Colors.white,
                )
              : null,
    );
  }
}

// ── Vista inicial: info del perfil antes de calcular ─────────────────────────
class _ProfileInfoView extends StatelessWidget {
  final AthleteProfile profile;
  final VoidCallback onCalculate;

  const _ProfileInfoView({required this.profile, required this.onCalculate});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Tarjeta de descripción
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(profile.emoji, style: const TextStyle(fontSize: 56)),
                  const SizedBox(height: 12),
                  Text(
                    profile.name,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    profile.description,
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Parámetros del perfil
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📋 Parámetros del perfil',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 12),
                  ...profile.perfil.entries.map(
                    (e) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Text(
                            '${e.key.replaceAll('_', ' ').toUpperCase()}: ',
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF1565C0),
                              fontSize: 13,
                            ),
                          ),
                          Expanded(
                            child: Text(
                              e.value,
                              style: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Info del servidor
          Card(
            color: Colors.grey.shade50,
            child: const Padding(
              padding: EdgeInsets.all(12),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.grey, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'El cálculo se realiza en el servidor local OptiCore '
                      '(FastAPI + SciPy HiGHS). Asegúrate de que INICIAR.bat '
                      'esté corriendo en tu PC.',
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 80), // espacio para FAB
        ],
      ),
    );
  }
}

// ── Tab 1: Receta ─────────────────────────────────────────────────────────────
class _RecipeTab extends StatelessWidget {
  final DietResult result;
  final NumberFormat currency;

  const _RecipeTab({required this.result, required this.currency});

  @override
  Widget build(BuildContext context) {
    // Ordenar por cantidad descendente, filtrar < 1g
    final items = result.solution.entries
        .where((e) => e.value > 0.001)
        .toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Tarjeta resumen de costo
        Card(
          color: Colors.green.shade50,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Estado', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    Text(
                      result.status == 'optimal' ? '✅ Óptimo' : result.status,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text('Costo por kg', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    Text(
                      '${currency.format(result.objectiveValue)} USD',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Colors.green.shade700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),

        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 4, vertical: 4),
          child: Text(
            'Receta óptima (g por kg de dieta):',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
          ),
        ),

        ...items.map((e) {
          final grams  = e.value * 1000;
          final db     = kAlimentosDB[e.key];
          final emoji  = kAlimentoEmoji[e.key] ?? '🍽️';
          final grupo  = kAlimentoGrupo[e.key] ?? '—';
          final pct    = (e.value * 100);
          final color  = _grupoColor(grupo);

          return Card(
            margin: const EdgeInsets.only(bottom: 6),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  Text(emoji, style: const TextStyle(fontSize: 28)),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          e.key.replaceAll('_', ' '),
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 2),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 1),
                              decoration: BoxDecoration(
                                color: color.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                grupo,
                                style: TextStyle(
                                    fontSize: 11,
                                    color: color,
                                    fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(width: 6),
                            if (db != null)
                              Text(
                                '${db['kcal']!.toStringAsFixed(0)} kcal/kg · '
                                '${db['prot']!.toStringAsFixed(0)}g prot/kg',
                                style: const TextStyle(
                                    fontSize: 11, color: Colors.grey),
                              ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: e.value.clamp(0.0, 1.0),
                          backgroundColor: Colors.grey.shade200,
                          color: color,
                          minHeight: 4,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${grams.toStringAsFixed(1)} g',
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 15),
                      ),
                      Text(
                        '${pct.toStringAsFixed(1)}%',
                        style: const TextStyle(
                            fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 80),
      ],
    );
  }

  Color _grupoColor(String grupo) => switch (grupo) {
    'CHO'   => Colors.orange.shade700,
    'PROT'  => Colors.blue.shade700,
    'SUP'   => Colors.purple.shade700,
    'LACT'  => Colors.teal.shade600,
    'GRASA' => Colors.green.shade700,
    'VEG'   => Colors.lightGreen.shade700,
    _       => Colors.grey,
  };
}

// ── Tab 2: Gráfico ────────────────────────────────────────────────────────────
class _ChartTab extends StatefulWidget {
  final DietResult result;
  const _ChartTab({required this.result});

  @override
  State<_ChartTab> createState() => _ChartTabState();
}

class _ChartTabState extends State<_ChartTab> {
  int _touchedIndex = -1;

  static const _colors = [
    Color(0xFF1565C0), Color(0xFFFF6F00), Color(0xFF2E7D32),
    Color(0xFFC62828), Color(0xFF6A1B9A), Color(0xFF00838F),
    Color(0xFFEF6C00), Color(0xFF283593), Color(0xFF00695C),
    Color(0xFF4E342E),
  ];

  @override
  Widget build(BuildContext context) {
    final items = widget.result.solution.entries
        .where((e) => e.value > 0.01)
        .toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Pie chart de composición
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    'Composición por Peso',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 220,
                    child: PieChart(
                      PieChartData(
                        pieTouchData: PieTouchData(
                          touchCallback: (evt, resp) {
                            setState(() {
                              _touchedIndex = resp?.touchedSection
                                      ?.touchedSectionIndex ??
                                  -1;
                            });
                          },
                        ),
                        sections: items.asMap().entries.map((e) {
                          final idx     = e.key;
                          final entry   = e.value;
                          final isTouched = idx == _touchedIndex;
                          final color   = _colors[idx % _colors.length];
                          return PieChartSectionData(
                            value:  entry.value * 100,
                            title:  isTouched
                                ? '${(entry.value * 100).toStringAsFixed(1)}%'
                                : '',
                            color:  color,
                            radius: isTouched ? 90 : 75,
                            titleStyle: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          );
                        }).toList(),
                        sectionsSpace: 2,
                        centerSpaceRadius: 36,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // FIX: Leyenda completa
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: items.asMap().entries.map((e) {
                      final color = _colors[e.key % _colors.length];
                      final emoji = kAlimentoEmoji[e.value.key] ?? '🍽️';
                      return Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 12, height: 12,
                            decoration: BoxDecoration(
                              color: color,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '$emoji ${e.value.key.replaceAll('_', ' ')} '
                            '(${(e.value.value * 100).toStringAsFixed(1)}%)',
                            style: const TextStyle(fontSize: 11),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Pie chart de macros en % kcal
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    'Distribución de Macronutrientes (% kcal)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 180,
                    child: PieChart(
                      PieChartData(
                        sections: [
                          PieChartSectionData(
                            value: widget.result.totals.pctProtKcal,
                            title: 'Prot\n${widget.result.totals.pctProtKcal.toStringAsFixed(0)}%',
                            color: const Color(0xFF1565C0),
                            radius: 70,
                            titleStyle: const TextStyle(
                                fontSize: 12, fontWeight: FontWeight.bold,
                                color: Colors.white),
                          ),
                          PieChartSectionData(
                            value: widget.result.totals.pctChoKcal,
                            title: 'CHO\n${widget.result.totals.pctChoKcal.toStringAsFixed(0)}%',
                            color: const Color(0xFFFF6F00),
                            radius: 70,
                            titleStyle: const TextStyle(
                                fontSize: 12, fontWeight: FontWeight.bold,
                                color: Colors.white),
                          ),
                          PieChartSectionData(
                            value: widget.result.totals.pctGrasaKcal,
                            title: 'Grasa\n${widget.result.totals.pctGrasaKcal.toStringAsFixed(0)}%',
                            color: const Color(0xFF2E7D32),
                            radius: 70,
                            titleStyle: const TextStyle(
                                fontSize: 12, fontWeight: FontWeight.bold,
                                color: Colors.white),
                          ),
                        ],
                        sectionsSpace: 3,
                        centerSpaceRadius: 0,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

// ── Tab 3: Totales nutricionales ──────────────────────────────────────────────
class _NutritionTab extends StatelessWidget {
  final DietResult result;
  final NumberFormat currency;

  const _NutritionTab({required this.result, required this.currency});

  @override
  Widget build(BuildContext context) {
    final t = result.totals;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Totales por kg de dieta
          _SectionTitle('Por kg de dieta (base normalizada)'),
          const SizedBox(height: 8),
          _NutRow('🔥 Energía',   '${t.kcal.toStringAsFixed(0)} kcal'),
          _NutRow('💪 Proteína',  '${t.protG.toStringAsFixed(1)} g'),
          _NutRow('⚡ Carbohidratos', '${t.choG.toStringAsFixed(1)} g'),
          _NutRow('🫒 Grasas',    '${t.grasaG.toStringAsFixed(1)} g'),
          _NutRow('🌾 Fibra',     '${t.fibraG.toStringAsFixed(1)} g'),
          _NutRow('🐟 Omega-3',   '${t.omega3G.toStringAsFixed(2)} g'),
          _NutRow('💰 Costo',     '${currency.format(t.costUsd)} USD'),
          const SizedBox(height: 16),

          // Estimado para día completo (2.5 kg/día)
          _SectionTitle('Estimado diario (2.5 kg de dieta/día)'),
          const SizedBox(height: 8),
          _NutRow('🔥 Energía total',   '${t.kcalDay.toStringAsFixed(0)} kcal/día',
              highlight: true),
          _NutRow('💪 Proteína total',  '${t.protGDay.toStringAsFixed(0)} g/día',
              highlight: true),
          _NutRow('⚡ CHO total',       '${t.choGDay.toStringAsFixed(0)} g/día',
              highlight: true),
          _NutRow('🫒 Grasas total',    '${t.grasaGDay.toStringAsFixed(0)} g/día'),
          _NutRow('💰 Costo diario',    '${currency.format(t.costDay)} USD/día',
              highlight: true),
          const SizedBox(height: 16),

          // % kcal macros
          _SectionTitle('Distribución calórica'),
          const SizedBox(height: 8),
          _NutRow('💪 % kcal Proteína',     '${t.pctProtKcal.toStringAsFixed(1)}%'),
          _NutRow('⚡ % kcal CHO',          '${t.pctChoKcal.toStringAsFixed(1)}%'),
          _NutRow('🫒 % kcal Grasas',       '${t.pctGrasaKcal.toStringAsFixed(1)}%'),
          const SizedBox(height: 16),

          // Solver info
          _SectionTitle('Información del solver'),
          const SizedBox(height: 8),
          _NutRow('Estado',    result.status),
          _NutRow('Solver',    result.solverUsed),
          _NutRow('Iteraciones',
              '${result.diagnostics['iterations'] ?? '-'}'),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle(this.text);

  @override
  Widget build(BuildContext context) => Text(
        text,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 15,
          color: Color(0xFF1565C0),
        ),
      );
}

class _NutRow extends StatelessWidget {
  final String label;
  final String value;
  final bool highlight;

  const _NutRow(this.label, this.value, {this.highlight = false});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 14)),
            Text(
              value,
              style: TextStyle(
                fontSize: 14,
                fontWeight:
                    highlight ? FontWeight.bold : FontWeight.w500,
                color: highlight
                    ? const Color(0xFF1565C0)
                    : Colors.black87,
              ),
            ),
          ],
        ),
      );
}

// ── Vista de error ────────────────────────────────────────────────────────────
class _ErrorView extends StatelessWidget {
  final String error;
  final VoidCallback onRetry;

  const _ErrorView({required this.error, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Card(
          color: Colors.red.shade50,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, color: Colors.red, size: 52),
                const SizedBox(height: 12),
                const Text(
                  'Error al calcular la dieta',
                  style: TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  error,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.red.shade700, fontSize: 13),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () => context.push('/settings'),
                      icon: const Icon(Icons.settings),
                      label: const Text('Ajustes'),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton.icon(
                      onPressed: onRetry,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Reintentar'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
