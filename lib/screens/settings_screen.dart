import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlCtrl;
  bool? _testResult;
  bool _testing = false;

  @override
  void initState() {
    super.initState();
    _urlCtrl = TextEditingController(text: ApiService.baseUrl);
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    super.dispose();
  }

  Future<void> _testConnection() async {
    ApiService.setBaseUrl(_urlCtrl.text.trim());
    setState(() { _testing = true; _testResult = null; });
    final ok = await ApiService.checkHealth();
    setState(() { _testing = false; _testResult = ok; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('⚙️ Configuración')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // URL del servidor
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '🌐 URL del servidor OptiCore',
                    style: TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Emulador Android: http://10.0.2.2:8000\n'
                    'Dispositivo físico: http://<IP-de-tu-PC>:8000\n'
                    'Ejemplo: http://192.168.1.100:8000',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _urlCtrl,
                    decoration: InputDecoration(
                      labelText: 'URL del servidor',
                      hintText: 'http://10.0.2.2:8000',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () => _urlCtrl.clear(),
                      ),
                    ),
                    keyboardType: TextInputType.url,
                    onChanged: (_) => setState(() => _testResult = null),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _testing ? null : _testConnection,
                          icon: _testing
                              ? const SizedBox(
                                  width: 16, height: 16,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2, color: Colors.white),
                                )
                              : const Icon(Icons.wifi_find),
                          label: Text(_testing
                              ? 'Probando...'
                              : 'Probar conexión'),
                        ),
                      ),
                    ],
                  ),
                  if (_testResult != null) ...[
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _testResult!
                            ? Colors.green.shade50
                            : Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _testResult!
                                ? Icons.check_circle
                                : Icons.cancel,
                            color: _testResult!
                                ? Colors.green
                                : Colors.red,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            _testResult!
                                ? '✅ Servidor disponible — conexión OK'
                                : '❌ No se pudo conectar. Verifica la IP y que INICIAR.bat esté corriendo.',
                            style: TextStyle(
                              color: _testResult!
                                  ? Colors.green.shade700
                                  : Colors.red.shade700,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Cómo encontrar la IP
          Card(
            color: Colors.blue.shade50,
            child: const Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '💡 Cómo encontrar la IP de tu PC',
                    style: TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  SizedBox(height: 8),
                  Text(
                    '1. En el PC donde corre INICIAR.bat:\n'
                    '2. Abre CMD y escribe: ipconfig\n'
                    '3. Busca "Dirección IPv4" (ej: 192.168.1.100)\n'
                    '4. Ingresa esa IP arriba: http://192.168.1.100:8000\n'
                    '5. Asegúrate de que tu teléfono y el PC '
                    'estén en la misma red WiFi.',
                    style: TextStyle(fontSize: 12, height: 1.5),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Acerca de
          Card(
            child: const Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Acerca de OptiCore Atletas',
                    style: TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  SizedBox(height: 8),
                  Text('Versión: 1.0.0', style: TextStyle(fontSize: 13)),
                  Text('Motor: SciPy HiGHS LP/MILP', style: TextStyle(fontSize: 13)),
                  Text('API: FastAPI + Uvicorn', style: TextStyle(fontSize: 13)),
                  Text(
                    'Base científica: ISSN 2017 · ACSM 2016 · '
                    'USDA FoodData Central · Thomas et al. 2016',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
