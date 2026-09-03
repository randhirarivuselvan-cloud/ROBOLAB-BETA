import 'package:flutter/material.dart';

void main() => runApp(const RoboLabApp());

class RoboLabApp extends StatelessWidget {
  const RoboLabApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'RoboLab',
        theme: ThemeData(useMaterial3: true, colorScheme: ColorScheme.fromSeed(seedColor: Colors.cyan, brightness: Brightness.dark)),
        home: const RoboLabHome(),
      );
}

class RoboLabHome extends StatefulWidget {
  const RoboLabHome({super.key});
  @override
  State<RoboLabHome> createState() => _RoboLabHomeState();
}

class _RoboLabHomeState extends State<RoboLabHome> {
  int tab = 0;
  final projects = <String>['New Robotics Project'];

  @override
  Widget build(BuildContext context) {
    final pages = [_home(), _projects(), const Workspace()];
    return Scaffold(
      appBar: AppBar(title: const Text('RoboLab', style: TextStyle(fontWeight: FontWeight.w900)), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.settings_outlined))]),
      body: pages[tab],
      bottomNavigationBar: NavigationBar(selectedIndex: tab, onDestinationSelected: (v) => setState(() => tab = v), destinations: const [
        NavigationDestination(icon: Icon(Icons.dashboard_outlined), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.folder_outlined), label: 'Projects'),
        NavigationDestination(icon: Icon(Icons.auto_awesome_outlined), label: 'AI Workspace'),
      ]),
    );
  }

  Widget _home() => ListView(padding: const EdgeInsets.all(20), children: [
        const Text('Build something real.', style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900)),
        const SizedBox(height: 8),
        Text('Describe a robot, circuit or embedded system in natural language.', style: TextStyle(color: Colors.grey.shade400, fontSize: 16)),
        const SizedBox(height: 24),
        FilledButton.icon(onPressed: () => setState(() => tab = 2), icon: const Icon(Icons.auto_awesome), label: const Text('Start with AI')),
        const SizedBox(height: 24),
        _card('Builder AI', Icons.account_tree_outlined, 'Turn an idea into a structured engineering project.'),
        _card('Circuit AI', Icons.memory_outlined, 'Plan components, connections and power requirements.'),
        _card('Code AI', Icons.code, 'Generate maintainable embedded firmware.'),
        _card('Verification', Icons.verified_outlined, 'Cross-check the project before final output.'),
      ]);

  Widget _projects() => ListView(padding: const EdgeInsets.all(20), children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Projects', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)), IconButton(onPressed: () => setState(() => projects.add('Untitled Project ${projects.length + 1}')), icon: const Icon(Icons.add_circle_outline))]),
        ...projects.map((p) => Card(child: ListTile(leading: const Icon(Icons.smart_toy_outlined), title: Text(p), subtitle: const Text('RoboLab project'), trailing: const Icon(Icons.chevron_right)))),
      ]);

  Widget _card(String title, IconData icon, String subtitle) => Card(margin: const EdgeInsets.only(bottom: 12), child: ListTile(contentPadding: const EdgeInsets.all(16), leading: CircleAvatar(child: Icon(icon)), title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)), subtitle: Text(subtitle)));
}

class Workspace extends StatefulWidget {
  const Workspace({super.key});
  @override
  State<Workspace> createState() => _WorkspaceState();
}

class _WorkspaceState extends State<Workspace> {
  final controller = TextEditingController();
  final stages = <String>[];
  bool running = false;

  Future<void> buildProject() async {
    if (controller.text.trim().isEmpty || running) return;
    setState(() { running = true; stages.clear(); });
    const pipeline = ['Understand requirements', 'Plan architecture', 'Validate components and power', 'Generate firmware structure', 'Run verification'];
    for (final stage in pipeline) {
      await Future<void>.delayed(const Duration(milliseconds: 300));
      if (!mounted) return;
      setState(() => stages.add(stage));
    }
    if (mounted) setState(() { running = false; stages.add('Draft ready — backend generation and compilation will plug into this pipeline.'); });
  }

  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: [
        const Text('AI Workspace', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
        const SizedBox(height: 8),
        const Text('One request → plan → circuit → code → verification.'),
        const SizedBox(height: 18),
        TextField(controller: controller, minLines: 5, maxLines: 8, decoration: const InputDecoration(hintText: 'Example: Build a line-following robot with Arduino, IR sensors and a motor driver.', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: buildProject, icon: running ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.play_arrow), label: Text(running ? 'Running pipeline…' : 'Build project')),
        const SizedBox(height: 20),
        if (stages.isNotEmpty) Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: stages.map((s) => Padding(padding: const EdgeInsets.symmetric(vertical: 6), child: Row(children: [Icon(s.startsWith('Draft') ? Icons.check_circle : Icons.circle_outlined, size: 18), const SizedBox(width: 10), Expanded(child: Text(s))]))).toList()))),
      ]);

  @override
  void dispose() { controller.dispose(); super.dispose(); }
}
