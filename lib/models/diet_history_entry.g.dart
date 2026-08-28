// GENERATED CODE - DO NOT MODIFY BY HAND
// Equivalente al output de: dart run build_runner build

part of 'diet_history_entry.dart';

class DietHistoryEntryAdapter extends TypeAdapter<DietHistoryEntry> {
  @override
  final int typeId = 0;

  @override
  DietHistoryEntry read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return DietHistoryEntry(
      profileId:    fields[0] as String,
      profileName:  fields[1] as String,
      date:         fields[2] as DateTime,
      costUsdPerKg: fields[3] as double,
      solution:     (fields[4] as Map).cast<String, double>(),
      kcalPerKg:    fields[5] as double,
      protGPerKg:   fields[6] as double,
      choGPerKg:    fields[7] as double,
      grasaGPerKg:  fields[8] as double,
    );
  }

  @override
  void write(BinaryWriter writer, DietHistoryEntry obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)..write(obj.profileId)
      ..writeByte(1)..write(obj.profileName)
      ..writeByte(2)..write(obj.date)
      ..writeByte(3)..write(obj.costUsdPerKg)
      ..writeByte(4)..write(obj.solution)
      ..writeByte(5)..write(obj.kcalPerKg)
      ..writeByte(6)..write(obj.protGPerKg)
      ..writeByte(7)..write(obj.choGPerKg)
      ..writeByte(8)..write(obj.grasaGPerKg);
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DietHistoryEntryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;

  @override
  int get hashCode => typeId.hashCode;
}
