// ── Base de datos nutricional (USDA FoodData Central) ────────────────────────
// Unidades: por kg de alimento
// kcal/kg · prot_g/kg · cho_g/kg · grasa_g/kg · fibra_g/kg · omega3_g/kg
const Map<String, Map<String, double>> kAlimentosDB = {
  'Avena':            {'kcal': 3890, 'prot': 131,  'cho': 668, 'grasa':  66, 'fibra': 100, 'omega3':  1.0, 'costo':  1.50},
  'Arroz_Blanco':     {'kcal': 3640, 'prot':  71,  'cho': 800, 'grasa':   6, 'fibra':   2, 'omega3':  0.1, 'costo':  1.20},
  'Batata':           {'kcal':  860, 'prot':  16,  'cho': 201, 'grasa':   1, 'fibra':  30, 'omega3':  0.1, 'costo':  1.80},
  'Quinoa':           {'kcal': 3680, 'prot': 141,  'cho': 640, 'grasa':  60, 'fibra':  70, 'omega3':  0.8, 'costo':  8.00},
  'Pan_Integral':     {'kcal': 2470, 'prot':  90,  'cho': 461, 'grasa':  31, 'fibra':  60, 'omega3':  0.5, 'costo':  3.00},
  'Platano':          {'kcal':  890, 'prot':  11,  'cho': 229, 'grasa':   3, 'fibra':  26, 'omega3':  0.3, 'costo':  1.50},
  'Pechuga_Pollo':    {'kcal': 1650, 'prot': 310,  'cho':   0, 'grasa':  36, 'fibra':   0, 'omega3':  0.2, 'costo':  8.00},
  'Atun_Lata':        {'kcal': 1160, 'prot': 260,  'cho':   0, 'grasa':  13, 'fibra':   0, 'omega3':  5.5, 'costo':  6.00},
  'Salmon':           {'kcal': 2080, 'prot': 200,  'cho':   0, 'grasa': 130, 'fibra':   0, 'omega3': 22.0, 'costo': 18.00},
  'Huevo_Entero':     {'kcal': 1430, 'prot': 126,  'cho':   7, 'grasa':  97, 'fibra':   0, 'omega3':  1.0, 'costo':  4.00},
  'Claras_Huevo':     {'kcal':  520, 'prot': 109,  'cho':   7, 'grasa':   2, 'fibra':   0, 'omega3':  0.1, 'costo':  5.00},
  'Proteina_Whey':    {'kcal': 3600, 'prot': 800,  'cho':  75, 'grasa':  30, 'fibra':   0, 'omega3':  1.0, 'costo': 25.00},
  'Caseina':          {'kcal': 3600, 'prot': 800,  'cho':  30, 'grasa':  10, 'fibra':   0, 'omega3':  1.0, 'costo': 28.00},
  'Leche_Descremada': {'kcal':  350, 'prot':  35,  'cho':  51, 'grasa':   1, 'fibra':   0, 'omega3':  0.1, 'costo':  1.00},
  'Yogur_Griego':     {'kcal':  590, 'prot': 100,  'cho':  38, 'grasa':   9, 'fibra':   0, 'omega3':  0.2, 'costo':  5.00},
  'Aceite_Oliva':     {'kcal': 8840, 'prot':   0,  'cho':   0, 'grasa':1000, 'fibra':   0, 'omega3':  1.0, 'costo': 12.00},
  'Almendras':        {'kcal': 5780, 'prot': 213,  'cho': 216, 'grasa': 500, 'fibra': 125, 'omega3':  0.4, 'costo': 14.00},
  'Brocoli':          {'kcal':  340, 'prot':  28,  'cho':  66, 'grasa':   4, 'fibra':  26, 'omega3':  0.2, 'costo':  3.00},
  'Espinaca':         {'kcal':  230, 'prot':  29,  'cho':  36, 'grasa':   4, 'fibra':  22, 'omega3':  0.5, 'costo':  4.00},
  'Manzana':          {'kcal':  520, 'prot':   3,  'cho': 138, 'grasa':   2, 'fibra':  24, 'omega3':  0.1, 'costo':  2.00},
};

// ── Grupo de cada alimento para color en gráfico ──────────────────────────────
const Map<String, String> kAlimentoGrupo = {
  'Avena': 'CHO',          'Arroz_Blanco': 'CHO',  'Batata': 'CHO',
  'Quinoa': 'CHO',         'Pan_Integral': 'CHO',   'Platano': 'CHO',
  'Pechuga_Pollo': 'PROT', 'Atun_Lata': 'PROT',    'Salmon': 'PROT',
  'Huevo_Entero': 'PROT',  'Claras_Huevo': 'PROT',
  'Proteina_Whey': 'SUP',  'Caseina': 'SUP',
  'Leche_Descremada': 'LACT', 'Yogur_Griego': 'LACT',
  'Aceite_Oliva': 'GRASA', 'Almendras': 'GRASA',
  'Brocoli': 'VEG',        'Espinaca': 'VEG',      'Manzana': 'VEG',
};

// ── Emoji de cada alimento ────────────────────────────────────────────────────
const Map<String, String> kAlimentoEmoji = {
  'Avena': '🌾',           'Arroz_Blanco': '🍚',   'Batata': '🍠',
  'Quinoa': '🌿',          'Pan_Integral': '🍞',    'Platano': '🍌',
  'Pechuga_Pollo': '🍗',   'Atun_Lata': '🐟',      'Salmon': '🐠',
  'Huevo_Entero': '🥚',    'Claras_Huevo': '🥛',
  'Proteina_Whey': '🥤',   'Caseina': '🧪',
  'Leche_Descremada': '🥛','Yogur_Griego': '🫙',
  'Aceite_Oliva': '🫒',    'Almendras': '🥜',
  'Brocoli': '🥦',         'Espinaca': '🥬',       'Manzana': '🍎',
};

// ── Modelo de perfil ──────────────────────────────────────────────────────────
class AthleteProfile {
  final String id;
  final String name;
  final String emoji;
  final String description;
  final Map<String, String> perfil;
  final Map<String, dynamic> payloadTemplate;

  const AthleteProfile({
    required this.id,
    required this.name,
    required this.emoji,
    required this.description,
    required this.perfil,
    required this.payloadTemplate,
  });
}

// ── Totales nutricionales calculados desde la solución ────────────────────────
class NutritionalTotals {
  final double kcal;
  final double protG;
  final double choG;
  final double grasaG;
  final double fibraG;
  final double omega3G;
  final double costUsd;

  const NutritionalTotals({
    required this.kcal,
    required this.protG,
    required this.choG,
    required this.grasaG,
    required this.fibraG,
    required this.omega3G,
    required this.costUsd,
  });

  // Porcentaje kcal de cada macro
  double get pctProtKcal => kcal > 0 ? (protG * 4 / kcal) * 100 : 0;
  double get pctChoKcal  => kcal > 0 ? (choG  * 4 / kcal) * 100 : 0;
  double get pctGrasaKcal=> kcal > 0 ? (grasaG * 9 / kcal) * 100 : 0;

  // Estimado para 2.5 kg/día de dieta total
  double get kcalDay   => kcal   * 2.5;
  double get protGDay  => protG  * 2.5;
  double get choGDay   => choG   * 2.5;
  double get grasaGDay => grasaG * 2.5;
  double get costDay   => costUsd * 2.5;

  static NutritionalTotals fromSolution(
    Map<String, double> solution,
    double objectiveValue,
  ) {
    double kcal = 0, prot = 0, cho = 0, grasa = 0, fibra = 0, omega3 = 0;
    for (final entry in solution.entries) {
      final db = kAlimentosDB[entry.key];
      if (db == null) continue;
      final kg = entry.value; // fracción de kg
      kcal   += db['kcal']!   * kg;
      prot   += db['prot']!   * kg;
      cho    += db['cho']!    * kg;
      grasa  += db['grasa']!  * kg;
      fibra  += db['fibra']!  * kg;
      omega3 += db['omega3']! * kg;
    }
    return NutritionalTotals(
      kcal:    kcal,
      protG:   prot,
      choG:    cho,
      grasaG:  grasa,
      fibraG:  fibra,
      omega3G: omega3,
      costUsd: objectiveValue,
    );
  }
}

// ── Resultado del solver ──────────────────────────────────────────────────────
class DietResult {
  final String status;
  final double objectiveValue;
  final Map<String, double> solution;
  final Map<String, dynamic> diagnostics;
  final String solverUsed;
  late final NutritionalTotals totals;

  DietResult({
    required this.status,
    required this.objectiveValue,
    required this.solution,
    required this.diagnostics,
    required this.solverUsed,
  }) {
    totals = NutritionalTotals.fromSolution(solution, objectiveValue);
  }

  factory DietResult.fromJson(Map<String, dynamic> json) {
    final sol = (json['solution'] as Map<String, dynamic>?)?.map(
      (k, v) => MapEntry(k, (v as num).toDouble()),
    ) ?? {};
    return DietResult(
      status:         json['status']          ?? 'unknown',
      objectiveValue: (json['objective_value'] ?? 0).toDouble(),
      solution:       sol,
      diagnostics:    json['diagnostics']     ?? {},
      solverUsed:     json['solver_used']     ?? 'unknown',
    );
  }

  Map<String, dynamic> toJson() => {
    'status':          status,
    'objective_value': objectiveValue,
    'solution':        solution,
    'diagnostics':     diagnostics,
    'solver_used':     solverUsed,
  };
}
