import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:intl/intl.dart';
import '../models/diet_history_entry.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final box = Hive.box<DietHistoryEntry>('diet_history');
    final currency = NumberFormat.currency(symbol: '\$', decimalDigits: 2);
    final dateFmt  = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('📋 Historial de Dietas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep),
            tooltip: 'Limpiar historial',
            onPressed: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Limpiar historial'),
                  content: const Text(
                      '¿Eliminar todos los registros guardados?'),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancelar')),
                    ElevatedButton(
                        onPressed: () => Navigator.pop(ctx, true),
                        child: const Text('Eliminar')),
                  ],
                ),
              );
              if (ok == true) await box.clear();
            },
          ),
        ],
      ),
      body: ValueListenableBuilder(
        valueListenable: box.listenable(),
        builder: (context, Box<DietHistoryEntry> b, _) {
          if (b.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'Aún no hay dietas calculadas.\nLos resultados se guardan automáticamente.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey, fontSize: 15),
                  ),
                ],
              ),
            );
          }

          // Más recientes primero
          final entries = b.values.toList()
            ..sort((a, b) => b.date.compareTo(a.date));

          return ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: entries.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (ctx, i) {
              final e = entries[i];
              return Card(
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  leading: CircleAvatar(
                    backgroundColor: Colors.blue.shade100,
                    child: Text(
                      _profileEmoji(e.profileId),
                      style: const TextStyle(fontSize: 22),
                    ),
                  ),
                  title: Text(
                    e.profileName.replaceAll(RegExp(r'^[^\w\s]+\s*'), ''),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Text(dateFmt.format(e.date),
                          style: const TextStyle(fontSize: 12)),
                      const SizedBox(height: 2),
                      Text(
                        '🔥 ${e.kcalPerKg.toStringAsFixed(0)} kcal/kg  '
                        '💪 ${e.protGPerKg.toStringAsFixed(0)} g prot/kg  '
                        '⚡ ${e.choGPerKg.toStringAsFixed(0)} g CHO/kg',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ],
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        currency.format(e.costUsdPerKg),
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade700,
                          fontSize: 15,
                        ),
                      ),
                      const Text(
                        'USD/kg',
                        style: TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }

  String _profileEmoji(String id) => switch (id) {
    'fuerza_volumen'    => '🏋️',
    'resistencia_cardio'=> '🚴',
    'definicion_corte'  => '✂️',
    'recuperacion_post' => '🔋',
    _                   => '🏅',
  };
}
