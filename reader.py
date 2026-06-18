import os
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# ========= БАЗА ИЗВЕСТНЫХ ЧИТОВ =========
CHEAT_DATABASE = {
    "wurst": {
        "name": "Wurst Client",
        "risk": "КРИТИЧНЫЙ",
        "description": "Один из самых популярных чит-клиентов. Содержит X-Ray, KillAura, FlyHack и другие читы.",
        "detection": "По названию мода или папки"
    },
    "impact": {
        "name": "Impact Client",
        "risk": "КРИТИЧНЫЙ",
        "description": "Мощный чит-клиент с множеством функций для PvP и гриферства.",
        "detection": "По названию мода или папки"
    },
    "meteor": {
        "name": "Meteor Client",
        "risk": "КРИТИЧНЫЙ",
        "description": "Популярный чит-клиент для версий 1.16+. Содержит Utility-модули.",
        "detection": "По названию мода или папки"
    },
    "liquidbounce": {
        "name": "LiquidBounce",
        "risk": "КРИТИЧНЫЙ",
        "description": "Чит-клиент с открытым исходным кодом. Имеет множество функций для обхода античитов.",
        "detection": "По названию мода"
    },
    "sigma": {
        "name": "Sigma Client",
        "risk": "КРИТИЧНЫЙ",
        "description": "Платный чит-клиент с хорошей скрытностью.",
        "detection": "По названию мода или папки"
    },
    "vape": {
        "name": "Vape",
        "risk": "ВЫСОКИЙ",
        "description": "Ghost-клиент, который не оставляет следов в папке с модами. Обнаруживается по инжектированным DLL.",
        "detection": "По инжектированным DLL или подозрительным папкам"
    },
    "injector": {
        "name": "Чит-инжектор",
        "risk": "ВЫСОКИЙ",
        "description": "Программа, внедряющая читы в процесс Minecraft.",
        "detection": "По обнаруженным DLL в процессе"
    },
    "xray": {
        "name": "X-Ray Resource Pack",
        "risk": "СРЕДНИЙ",
        "description": "Ресурспак, делающий руду видимой сквозь стены.",
        "detection": "По названию ресурспака"
    },
    "aimbot": {
        "name": "Aimbot",
        "risk": "ВЫСОКИЙ",
        "description": "Автоматическое наведение на игроков.",
        "detection": "По названию мода или DLL"
    },
    "killaura": {
        "name": "KillAura",
        "risk": "КРИТИЧНЫЙ",
        "description": "Автоматическая атака игроков вокруг.",
        "detection": "По названию мода или DLL"
    },
    "flyhack": {
        "name": "Fly Hack",
        "risk": "КРИТИЧНЫЙ",
        "description": "Позволяет летать на сервере.",
        "detection": "По названию мода или DLL"
    },
    "speedhack": {
        "name": "Speed Hack",
        "risk": "КРИТИЧНЫЙ",
        "description": "Увеличивает скорость передвижения.",
        "detection": "По названию мода или DLL"
    },
    "scaffold": {
        "name": "Scaffold",
        "risk": "СРЕДНИЙ",
        "description": "Автоматическая постройка мостов.",
        "detection": "По названию мода"
    },
    "freecam": {
        "name": "FreeCam",
        "risk": "СРЕДНИЙ",
        "description": "Позволяет осматривать местность без перемещения игрока.",
        "detection": "По названию мода"
    },
    "clickgui": {
        "name": "ClickGUI",
        "risk": "ИНФОРМАТИВНЫЙ",
        "description": "Меню настроек чита, само по себе не является читом.",
        "detection": "Признак наличия чита"
    },
    "alts": {
        "name": "Alt Manager",
        "risk": "СРЕДНИЙ",
        "description": "Папка с альтернативными аккаунтами для обхода банов.",
        "detection": "По подозрительной папке"
    },
    "proxy": {
        "name": "Proxy Manager",
        "risk": "СРЕДНИЙ",
        "description": "Папка с прокси для обхода IP-банов.",
        "detection": "По подозрительной папке"
    }
}

class SCMReportReader:
    def __init__(self, root):
        self.root = root
        self.root.title("SCM Report Reader - Анализ отчётов")
        self.root.geometry("1000x700")
        
        self.report_data = None
        self.report_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(top_frame, text="📂 Открыть отчёт", command=self.open_report, padx=20).pack(side='left', padx=5)
        tk.Button(top_frame, text="🔄 Обновить анализ", command=self.analyze_report, padx=20).pack(side='left', padx=5)
        
        self.file_label = tk.Label(top_frame, text="Файл не выбран", anchor='w')
        self.file_label.pack(side='left', fill='x', expand=True, padx=10)
        
        # Основные вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладка "Обнаружено читов"
        self.detected_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detected_frame, text="⚠️ ОБНАРУЖЕНО ЧИТОВ")
        self.create_detected_tab()
        
        # Вкладка "Все моды"
        self.mods_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mods_frame, text="🧩 Все моды")
        self.create_mods_tab()
        
        # Вкладка "Подозрительные папки"
        self.folders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.folders_frame, text="📁 Подозрительные папки")
        self.create_folders_tab()
        
        # Вкладка "Инжектированные DLL"
        self.injected_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.injected_frame, text="💉 Инжектированные DLL")
        self.create_injected_tab()
        
        # Вкладка "Информация об отчёте"
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="ℹ️ Информация")
        self.create_info_tab()
        
        # Статус бар
        self.status_bar = tk.Label(self.root, text="Готов к работе", bd=1, relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', side='bottom')
    
    def create_detected_tab(self):
        # Таблица с найденными читами
        self.detected_tree = ttk.Treeview(self.detected_frame, columns=('type', 'name', 'risk', 'description', 'detection'), show='headings')
        self.detected_tree.heading('type', text='Тип')
        self.detected_tree.heading('name', text='Название')
        self.detected_tree.heading('risk', text='Уровень риска')
        self.detected_tree.heading('description', text='Описание')
        self.detected_tree.heading('detection', text='Способ обнаружения')
        
        self.detected_tree.column('type', width=100)
        self.detected_tree.column('name', width=150)
        self.detected_tree.column('risk', width=100)
        self.detected_tree.column('description', width=300)
        self.detected_tree.column('detection', width=200)
        
        self.detected_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Настройка цветов для рисков
        self.detected_tree.tag_configure('critical', background='#662222', foreground='#ff8888')
        self.detected_tree.tag_configure('high', background='#664422', foreground='#ffaa66')
        self.detected_tree.tag_configure('medium', background='#336633', foreground='#aaffaa')
        self.detected_tree.tag_configure('info', background='#333366', foreground='#aaaaff')
    
    def create_mods_tab(self):
        self.mods_tree = ttk.Treeview(self.mods_frame, columns=('name', 'status', 'path'), show='headings')
        self.mods_tree.heading('name', text='Название мода')
        self.mods_tree.heading('status', text='Статус')
        self.mods_tree.heading('path', text='Путь')
        self.mods_tree.column('name', width=250)
        self.mods_tree.column('status', width=100)
        self.mods_tree.column('path', width=500)
        self.mods_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.mods_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
    
    def create_folders_tab(self):
        self.folders_tree = ttk.Treeview(self.folders_frame, columns=('name', 'path'), show='headings')
        self.folders_tree.heading('name', text='Название папки')
        self.folders_tree.heading('path', text='Путь')
        self.folders_tree.column('name', width=300)
        self.folders_tree.column('path', width=550)
        self.folders_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.folders_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
    
    def create_injected_tab(self):
        self.injected_tree = ttk.Treeview(self.injected_frame, columns=('name', 'status', 'path'), show='headings')
        self.injected_tree.heading('name', text='Название DLL')
        self.injected_tree.heading('status', text='Статус')
        self.injected_tree.heading('path', text='Путь')
        self.injected_tree.column('name', width=300)
        self.injected_tree.column('status', width=100)
        self.injected_tree.column('path', width=450)
        self.injected_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.injected_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
    
    def create_info_tab(self):
        self.info_text = scrolledtext.ScrolledText(self.info_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.info_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def open_report(self):
        file_path = filedialog.askopenfilename(
            title="Выберите отчёт SCM Scanner",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.report_file = file_path
            self.file_label.config(text=f"📄 {os.path.basename(file_path)}")
            self.load_report()
    
    def load_report(self):
        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            self.status_bar.config(text=f"Загружен отчёт: {os.path.basename(self.report_file)}")
            self.analyze_report()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчёт:\n{e}")
            self.status_bar.config(text="Ошибка загрузки отчёта")
    
    def analyze_report(self):
        if not self.report_data:
            messagebox.showwarning("Предупреждение", "Сначала загрузите отчёт")
            return
        
        detected_cheats = []
        
        # Анализ модов
        for mod in self.report_data.get('mods', []):
            mod_name_lower = mod['name'].lower()
            for cheat_key, cheat_info in CHEAT_DATABASE.items():
                if cheat_key in mod_name_lower:
                    detected_cheats.append({
                        'type': 'Мод',
                        'name': mod['name'],
                        'risk': cheat_info['risk'],
                        'description': cheat_info['description'],
                        'detection': cheat_info['detection']
                    })
                    break
            else:
                if mod.get('suspicious', False):
                    detected_cheats.append({
                        'type': 'Мод',
                        'name': mod['name'],
                        'risk': 'НЕИЗВЕСТНЫЙ',
                        'description': 'Подозрительный мод, не найденный в базе',
                        'detection': 'По ключевым словам'
                    })
        
        # Анализ папок
        for folder in self.report_data.get('suspicious_folders', []):
            folder_name_lower = folder['name'].lower()
            for cheat_key, cheat_info in CHEAT_DATABASE.items():
                if cheat_key in folder_name_lower:
                    detected_cheats.append({
                        'type': 'Папка',
                        'name': folder['name'],
                        'risk': cheat_info['risk'],
                        'description': cheat_info['description'],
                        'detection': cheat_info['detection']
                    })
                    break
            else:
                detected_cheats.append({
                    'type': 'Папка',
                    'name': folder['name'],
                    'risk': 'ПОДОЗРИТЕЛЬНАЯ',
                    'description': 'Подозрительная папка, не найденная в базе',
                    'detection': 'По ключевым словам'
                })
        
        # Анализ инжектированных DLL
        for dll in self.report_data.get('injected_dlls', []):
            dll_name_lower = dll['name'].lower()
            if dll.get('suspicious', False):
                detected_cheats.append({
                    'type': 'Инжект',
                    'name': dll['name'],
                    'risk': 'КРИТИЧНЫЙ',
                    'description': 'Обнаружен инжектированный DLL файл',
                    'detection': 'По наличию в процессе Minecraft'
                })
        
        # Обновляем таблицу обнаруженных читов
        for item in self.detected_tree.get_children():
            self.detected_tree.delete(item)
        
        for cheat in detected_cheats:
            risk = cheat['risk']
            tag = 'critical'
            if risk == 'ВЫСОКИЙ':
                tag = 'high'
            elif risk == 'СРЕДНИЙ':
                tag = 'medium'
            elif risk == 'ИНФОРМАТИВНЫЙ':
                tag = 'info'
            
            self.detected_tree.insert('', tk.END, values=(
                cheat['type'], cheat['name'], cheat['risk'], 
                cheat['description'], cheat['detection']
            ), tags=(tag,))
        
        # Обновляем вкладку с модами
        for item in self.mods_tree.get_children():
            self.mods_tree.delete(item)
        
        for mod in self.report_data.get('mods', []):
            status = "⚠️ ПОДОЗРИТЕЛЬНЫЙ" if mod.get('suspicious', False) else "✅ Обычный"
            item = self.mods_tree.insert('', tk.END, values=(mod['name'], status, mod['path']))
            if mod.get('suspicious', False):
                self.mods_tree.item(item, tags=('suspicious',))
        
        # Обновляем вкладку с папками
        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)
        
        for folder in self.report_data.get('suspicious_folders', []):
            item = self.folders_tree.insert('', tk.END, values=(folder['name'], folder['path']))
            self.folders_tree.item(item, tags=('suspicious',))
        
        # Обновляем вкладку с инжектированными DLL
        for item in self.injected_tree.get_children():
            self.injected_tree.delete(item)
        
        for dll in self.report_data.get('injected_dlls', []):
            status = "⚠️ ПОДОЗРИТЕЛЬНАЯ" if dll.get('suspicious', False) else "✅ Обычная"
            item = self.injected_tree.insert('', tk.END, values=(dll['name'], status, dll['path']))
            if dll.get('suspicious', False):
                self.injected_tree.item(item, tags=('suspicious',))
        
        # Обновляем информационную вкладку
        self.info_text.delete(1.0, tk.END)
        
        summary = self.report_data.get('summary', {})
        scan_info = self.report_data.get('scan_info', {})
        server_info = self.report_data.get('server_info', {})
        
        info_string = f"""
══════════════════════════════════════════════════════════════
              SCM REPORT READER - АНАЛИЗ ОТЧЁТА                
══════════════════════════════════════════════════════════════
                                                              
  📄 Файл: {os.path.basename(self.report_file)}                 
  ⏰ Время сканирования: {scan_info.get('timestamp', 'Неизвестно')}     
  📁 Папка Minecraft: {scan_info.get('minecraft_folder', 'Неизвестно')}  
  🌐 Сервер: {server_info.get('ip', 'Неизвестно')}:{server_info.get('port', '')}            
                                                              
══════════════════════════════════════════════════════════════
                      СТАТИСТИКА                               
══════════════════════════════════════════════════════════════
                                                              
  📦 Версий: {summary.get('total_versions', 0)}                                             
  🧩 Модов: {summary.get('total_mods', 0)} (подозрительных: {summary.get('suspicious_mods', 0)})                    
  🎨 Ресурспаков: {summary.get('total_resourcepacks', 0)}                                           
  🔧 DLL файлов: {summary.get('total_dll_files', 0)} (подозрительных: {summary.get('suspicious_dll_files', 0)})                 
  📁 Подозрительных папок: {summary.get('suspicious_folders', 0)}                                        
  💉 Инжектированных DLL: {summary.get('injected_dlls', 0)} (подозрительных: {summary.get('suspicious_injected', 0)})               
                                                              
══════════════════════════════════════════════════════════════
                      РЕЗУЛЬТАТ
══════════════════════════════════════════════════════════════
                                                              
  ⚠️ Обнаружено читов: {len(detected_cheats)}                                            
                                                              
══════════════════════════════════════════════════════════════
        """
        
        self.info_text.insert('1.0', info_string)
        
        self.status_bar.config(text=f"Анализ завершён. Обнаружено читов: {len(detected_cheats)}")
        
        # Показываем предупреждение если есть читы
        if detected_cheats:
            messagebox.showwarning("Обнаружены читы!", 
                f"В отчёте найдено {len(detected_cheats)} подозрительных объектов!\n"
                f"Рекомендуется принять меры.")

if __name__ == '__main__':
    root = tk.Tk()
    app = SCMReportReader(root)
    root.mainloop()
