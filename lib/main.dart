import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'screens/profile_selection_screen.dart';
import 'screens/diet_result_screen.dart';
import 'screens/history_screen.dart';
import 'screens/settings_screen.dart';
import 'models/diet_history_entry.dart';

// ── Router ────────────────────────────────────────────────────────────────────
final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const ProfileSelectionScreen(),
    ),
    GoRoute(
      path: '/diet/:profileId',
      builder: (context, state) {
        final profileId = state.pathParameters['profileId']!;
        return DietResultScreen(profileId: profileId);
      },
    ),
    GoRoute(
      path: '/history',
      builder: (context, state) => const HistoryScreen(),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);

// ── Entry point ───────────────────────────────────────────────────────────────
// FIX: main() debe ser async para inicializar Hive antes de runApp()
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar Hive para persistencia offline del historial
  await Hive.initFlutter();
  Hive.registerAdapter(DietHistoryEntryAdapter());
  await Hive.openBox<DietHistoryEntry>('diet_history');

  runApp(const OptiCoreApp());
}

class OptiCoreApp extends StatelessWidget {
  const OptiCoreApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'OptiCore Atletas',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1565C0),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        cardTheme: CardTheme(
          elevation: 3,
          shadowColor: Colors.blue.shade100,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
          backgroundColor: Color(0xFF1565C0),
          foregroundColor: Colors.white,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1565C0),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
          ),
        ),
      ),
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}
