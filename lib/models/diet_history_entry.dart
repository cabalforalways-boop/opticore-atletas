import 'package:hive/hive.dart';

part 'diet_history_entry.g.dart';

@HiveType(typeId: 0)
class DietHistoryEntry extends HiveObject {
  @HiveField(0)
  final String profileId;

  @HiveField(1)
  final String profileName;

  @HiveField(2)
  final DateTime date;

  @HiveField(3)
  final double costUsdPerKg;

  @HiveField(4)
  final Map<String, double> solution;

  @HiveField(5)
  final double kcalPerKg;

  @HiveField(6)
  final double protGPerKg;

  @HiveField(7)
  final double choGPerKg;

  @HiveField(8)
  final double grasaGPerKg;

  DietHistoryEntry({
    required this.profileId,
    required this.profileName,
    required this.date,
    required this.costUsdPerKg,
    required this.solution,
    required this.kcalPerKg,
    required this.protGPerKg,
    required this.choGPerKg,
    required this.grasaGPerKg,
  });
}
