import os
import sys
import platform
import json
import hashlib
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, colorchooser
import pickle
import re
from datetime import datetime

# Проверка наличия psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ========= ФИКСИРОВАННЫЕ СПИСКИ ПОДОЗРИТЕЛЬНЫХ СЛОВ =========
SUSPECT_MOD_KEYWORDS = [
    'wurst', 'impact', 'salhack', 'future', 'kappa', 'aristois', 'cheat', 'hack',
    'clickgui', 'xray', 'aimbot', 'killaura', 'nuker', 'scaffold', 'flyhack',
    'speedhack', 'freecam', 'ghost', 'vape', 'sigma', 'meteor', 'liquidbounce',
    'inertia', 'exhibition', 'novoline', 'rise', 'raven', 'itami', 'remix',
    'zero', 'nightmare', 'lunar', 'badlion'
]

SUSPECT_DLL_KEYWORDS = [
    'injector', 'cheat', 'hack', 'wallhack', 'aimbot', 'esp', 'triggerbot',
    'inject', 'bypass', 'stealth', 'recode', 'dllinject', 'hook', 'detour'
]

SUSPECT_FOLDER_KEYWORDS = [
    'wurst', 'impact', 'salhack', 'future', 'kappa', 'aristois', 'cheat', 'hack',
    'clickgui', 'xray', 'aimbot', 'killaura', 'nuker', 'scaffold', 'flyhack',
    'speedhack', 'freecam', 'ghost', 'vape', 'sigma', 'meteor', 'liquidbounce',
    'inertia', 'exhibition', 'novoline', 'rise', 'raven', 'itami', 'remix',
    'zero', 'nightmare', 'lunar', 'badlion', 'client', 'utility', 'exploit',
    'bypass', 'inject', 'auto', 'clicker', 'triggerbot', 'esp', 'wallhack',
    'reach', 'velocity', 'antibot', 'autocrystal', 'config', 'profiles',
    'alts', 'accounts', 'proxy', 'proxies', 'settings'
]

# ========= ХЕШИ ИЗВЕСТНЫХ ЧИТОВ =========
KNOWN_CHEAT_HASHES = {
    "wurst": {
        "hashes": ["5e8f7c9b6a3d2f1e4c5b6a7d8e9f0a1b", "wurst_7.0.jar"],
        "info": "Wurst Client - популярный чит-клиент"
    },
    "impact": {
        "hashes": ["impact_4.10.jar", "impact_4.9.jar"],
        "info": "Impact Client - чит-клиент с множеством функций"
    },
    "meteor": {
        "hashes": ["meteor-client-0.5.0.jar"],
        "info": "Meteor Client - чит-клиент для новых версий"
    },
    "liquidbounce": {
        "hashes": ["LiquidBounce.jar"],
        "info": "LiquidBounce - популярный чит-клиент"
    },
    "vape": {
        "hashes": ["vape.jar", "vape.dll"],
        "info": "Vape - Ghost-клиент (инжектор)"
    }
}

# ========= ТЕМЫ (сокращённо) =========
PRESET_THEMES = {
    "Тёмная": {
        "bg": "#2b2b2b", "fg": "#ffffff", "select_bg": "#0e639c", "select_fg": "#ffffff",
        "tree_bg": "#1e1e1e", "tree_fg": "#d4d4d4", "button_bg": "#3c3c3c", "button_fg": "#ffffff",
        "notebook_bg": "#252526", "status_bg": "#3c3c3c", "accent": "#0e639c",
        "suspicious_bg": "#662222", "suspicious_fg": "#ff8888"
    },
    "Светлая": {
        "bg": "#f0f0f0", "fg": "#000000", "select_bg": "#0078d7", "select_fg": "#ffffff",
        "tree_bg": "#ffffff", "tree_fg": "#000000", "button_bg": "#e1e1e1", "button_fg": "#000000",
        "notebook_bg": "#f0f0f0", "status_bg": "#e1e1e1", "accent": "#0078d7",
        "suspicious_bg": "#ffcccc", "suspicious_fg": "#cc0000"
    }
}

CONFIG_FILE = Path.home() / 'SCM_Scanner_Config.pkl'

def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'rb') as f:
                config = pickle.load(f)
                return config
    except:
        pass
    return {'theme': 'Тёмная', 'minecraft_path': None}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'wb') as f:
            pickle.dump(config, f)
    except:
        pass

def get_current_minecraft_server():
    # Упрощённая версия для краткости
    return 'Не определён', ''

def find_minecraft_folder():
    if sys.platform == 'win32':
        appdata = os.getenv('APPDATA', '')
        path = Path(appdata) / '.minecraft'
        if path.exists():
            return str(path)
    return None

def is_suspicious_mod(mod_name):
    mod_lower = mod_name.lower()
    for kw in SUSPECT_MOD_KEYWORDS:
        if kw.lower() in mod_lower:
            return True
    return False

def is_suspicious_dll(dll_name):
    dll_lower = dll_name.lower()
    for kw in SUSPECT_DLL_KEYWORDS:
        if kw.lower() in dll_lower:
            return True
    return False

def is_suspicious_folder(folder_name):
    folder_lower = folder_name.lower()
    for kw in SUSPECT_FOLDER_KEYWORDS:
        if kw.lower() in folder_lower:
            return True
    return False

def get_versions(minecraft_dir):
    versions = []
    versions_dir = Path(minecraft_dir) / 'versions'
    if versions_dir.exists():
        for v in versions_dir.iterdir():
            if v.is_dir():
                versions.append(v.name)
    return sorted(versions, reverse=True)

def get_mods(minecraft_dir):
    mods = []
    mods_dir = Path(minecraft_dir) / 'mods'
    if mods_dir.exists():
        for mod in mods_dir.glob('*.jar'):
            mods.append({'name': mod.name, 'path': str(mod), 'suspicious': is_suspicious_mod(mod.name)})
    return mods

def get_resourcepacks(minecraft_dir):
    packs = []
    respacks_dir = Path(minecraft_dir) / 'resourcepacks'
    if respacks_dir.exists():
        for pack in respacks_dir.iterdir():
            packs.append(pack.name)
    return packs

def get_dll_files(minecraft_dir):
    dlls = []
    minecraft_path = Path(minecraft_dir)
    if minecraft_path.exists():
        for dll in minecraft_path.rglob('*.dll'):
            try:
                dlls.append({'name': str(dll.relative_to(minecraft_path)), 'full_path': str(dll), 'suspicious': is_suspicious_dll(dll.name)})
            except:
                pass
    return dlls

def get_suspicious_folders(minecraft_dir):
    suspicious_folders = []
    minecraft_path = Path(minecraft_dir)
    if minecraft_path.exists():
        for item in minecraft_path.iterdir():
            if item.is_dir() and is_suspicious_folder(item.name):
                suspicious_folders.append({'name': item.name, 'path': str(item), 'suspicious': True})
            elif item.is_dir():
                for subitem in item.iterdir():
                    if subitem.is_dir() and is_suspicious_folder(subitem.name):
                        suspicious_folders.append({'name': f"{item.name}/{subitem.name}", 'path': str(subitem), 'suspicious': True})
    return suspicious_folders

def find_minecraft_process():
    if not PSUTIL_AVAILABLE:
        return None
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'].lower() in ['javaw.exe', 'java.exe']:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'minecraft' in cmdline.lower():
                    return proc
        except:
            continue
    return None

def get_injected_dlls(process):
    if not PSUTIL_AVAILABLE or sys.platform != 'win32':
        return [], 0, 0
    dlls = []
    suspicious_count = 0
    try:
        for mmap in process.memory_maps(grouped=False):
            if mmap.path and mmap.path.lower().endswith('.dll'):
                suspicious = is_suspicious_dll(os.path.basename(mmap.path))
                if suspicious:
                    suspicious_count += 1
                dlls.append({'name': os.path.basename(mmap.path), 'path': mmap.path, 'suspicious': suspicious})
    except:
        return [], 0, 0
    return dlls, len(dlls), suspicious_count

def export_report(minecraft_dir, versions, mods, packs, dll_files, suspicious_folders, injected_dlls, total_suspicious):
    """Экспортирует отчёт в JSON файл на диск C:\SCM"""
    
    # Создаём отчёт
    report = {
        "scan_info": {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "minecraft_folder": minecraft_dir,
            "scanner_version": "2.1"
        },
        "server_info": {
            "ip": get_current_minecraft_server()[0],
            "port": get_current_minecraft_server()[1]
        },
        "summary": {
            "total_versions": len(versions),
            "total_mods": len(mods),
            "suspicious_mods": len([m for m in mods if m['suspicious']]),
            "total_resourcepacks": len(packs),
            "total_dll_files": len(dll_files),
            "suspicious_dll_files": len([d for d in dll_files if d['suspicious']]),
            "suspicious_folders": len(suspicious_folders),
            "injected_dlls": len(injected_dlls),
            "suspicious_injected": len([d for d in injected_dlls if d['suspicious']])
        },
        "versions": versions,
        "mods": mods,
        "resourcepacks": packs,
        "dll_files": dll_files,
        "suspicious_folders": suspicious_folders,
        "injected_dlls": injected_dlls
    }
    
    # Папка для сохранения: C:\SCM
    save_folder = Path('C:/SCM')
    
    # Создаём папку, если её нет
    if not save_folder.exists():
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            print(f"Папка создана: {save_folder}")
        except Exception as e:
            print(f"Ошибка создания папки: {e}")
            # Если не удалось создать на C:\, сохраняем в папку с программой
            save_folder = Path(os.getcwd()) / 'SCM_Reports'
            if not save_folder.exists():
                save_folder.mkdir(parents=True, exist_ok=True)
    
    # Имя файла с датой и временем
    filename = save_folder / f"SCM_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Сохраняем файл
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return str(filename)
    except Exception as e:
        # Если ошибка, сохраняем в корень C:\
        try:
            filename = Path('C:/') / f"SCM_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return str(filename)
        except:
            # Последний шанс - папка с программой
            filename = Path(os.getcwd()) / f"SCM_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return str(filename)
# ========= ГЛАВНОЕ ПРИЛОЖЕНИЕ =========
class SCMScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("SCM - Scanner Cheat in Minecraft")
        self.root.geometry("1100x750")
        
        self.config = load_config()
        
        saved_path = self.config.get('minecraft_path')
        if saved_path and Path(saved_path).exists():
            self.minecraft_dir = saved_path
        else:
            self.minecraft_dir = find_minecraft_folder()
        
        if not self.minecraft_dir:
            folder = filedialog.askdirectory(title="Выберите папку .minecraft")
            if folder:
                self.minecraft_dir = folder
            else:
                messagebox.showerror("Ошибка", "Папка не выбрана")
                self.root.destroy()
                return
        
        self.setup_ui()
        self.refresh_all()
    
    def setup_ui(self):
        # Верхняя панель
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill='x', padx=5, pady=5)
        
        self.info_label = tk.Label(self.top_frame, text=f"📁 {self.minecraft_dir}", anchor='w')
        self.info_label.pack(side='left', fill='x', expand=True, padx=5)
        
        export_btn = tk.Button(self.top_frame, text="📄 Экспорт отчёта", command=self.export_report, padx=15)
        export_btn.pack(side='right', padx=2)
        
        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Версии
        self.versions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.versions_frame, text="📦 Версии")
        self.versions_listbox = tk.Listbox(self.versions_frame, font=('Consolas', 10))
        self.versions_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Моды
        self.mods_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mods_frame, text="🧩 Моды")
        self.mods_tree = ttk.Treeview(self.mods_frame, columns=('name', 'status', 'path'), show='headings')
        self.mods_tree.heading('name', text='Название мода')
        self.mods_tree.heading('status', text='Статус')
        self.mods_tree.heading('path', text='Путь')
        self.mods_tree.column('name', width=250)
        self.mods_tree.column('status', width=100)
        self.mods_tree.column('path', width=500)
        self.mods_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.mods_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
        
        # Ресурспаки
        self.resp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.resp_frame, text="🎨 Ресурспаки")
        self.resp_listbox = tk.Listbox(self.resp_frame, font=('Consolas', 10))
        self.resp_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # DLL файлы
        self.dll_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dll_frame, text="🔧 DLL файлы")
        self.dll_tree = ttk.Treeview(self.dll_frame, columns=('name', 'status', 'path'), show='headings')
        self.dll_tree.heading('name', text='DLL файл')
        self.dll_tree.heading('status', text='Статус')
        self.dll_tree.heading('path', text='Путь')
        self.dll_tree.column('name', width=250)
        self.dll_tree.column('status', width=100)
        self.dll_tree.column('path', width=500)
        self.dll_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.dll_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
        
        # Подозрительные папки
        self.folders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.folders_frame, text="📁 Подозрительные папки")
        self.folders_tree = ttk.Treeview(self.folders_frame, columns=('name', 'path'), show='headings')
        self.folders_tree.heading('name', text='Название папки')
        self.folders_tree.heading('path', text='Путь')
        self.folders_tree.column('name', width=300)
        self.folders_tree.column('path', width=550)
        self.folders_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.folders_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
        
        # Инжектированные DLL
        self.injected_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.injected_frame, text="💉 Инжектированные DLL")
        self.injected_status = tk.Label(self.injected_frame, text="Статус: ожидание...")
        self.injected_status.pack(fill='x', padx=5, pady=5)
        self.injected_tree = ttk.Treeview(self.injected_frame, columns=('name', 'status', 'path'), show='headings')
        self.injected_tree.heading('name', text='Название DLL')
        self.injected_tree.heading('status', text='Статус')
        self.injected_tree.heading('path', text='Путь')
        self.injected_tree.column('name', width=300)
        self.injected_tree.column('status', width=100)
        self.injected_tree.column('path', width=450)
        self.injected_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.injected_tree.tag_configure('suspicious', background='#662222', foreground='#ff8888')
        
        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="🔄 Обновить всё", command=self.refresh_all, padx=20).pack(side='left')
        tk.Button(btn_frame, text="🔍 Сканировать инжект", command=self.scan_injected, padx=20).pack(side='left')
        
        self.status_bar = tk.Label(self.root, text="Готов к работе", bd=1, relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', side='bottom')
    
    def export_report(self):
        """Экспортирует отчёт в файл"""
        try:
            # Собираем данные
            versions = get_versions(self.minecraft_dir)
            mods = get_mods(self.minecraft_dir)
            packs = get_resourcepacks(self.minecraft_dir)
            dll_files = get_dll_files(self.minecraft_dir)
            suspicious_folders = get_suspicious_folders(self.minecraft_dir)
            
            # Инжектированные DLL
            proc = find_minecraft_process()
            injected_dlls = []
            if proc:
                injected_dlls, _, _ = get_injected_dlls(proc)
            
            # Экспортируем
            filename = export_report(self.minecraft_dir, versions, mods, packs, dll_files, suspicious_folders, injected_dlls, 0)
            
            messagebox.showinfo("Успех", f"Отчёт сохранён:\n{filename}")
            self.status_bar.config(text=f"Отчёт экспортирован: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчёт:\n{e}")
    
    def scan_injected(self):
        for item in self.injected_tree.get_children():
            self.injected_tree.delete(item)
        
        if not PSUTIL_AVAILABLE:
            self.injected_status.config(text="❌ psutil не установлен!")
            return
        
        proc = find_minecraft_process()
        if not proc:
            self.injected_status.config(text="❌ Minecraft не запущен!")
            return
        
        dlls, total, suspicious = get_injected_dlls(proc)
        
        for dll in dlls:
            status = "⚠️ ПОДОЗРИТЕЛЬНАЯ" if dll['suspicious'] else "✅ Обычная"
            item = self.injected_tree.insert('', tk.END, values=(dll['name'], status, dll['path']))
            if dll['suspicious']:
                self.injected_tree.item(item, tags=('suspicious',))
        
        self.injected_status.config(text=f"✅ Найдено DLL: {total} | Подозрительных: {suspicious}")
    
    def refresh_all(self):
        self.status_bar.config(text="Обновление...")
        self.root.update()
        
        # Версии
        self.versions_listbox.delete(0, tk.END)
        for ver in get_versions(self.minecraft_dir):
            self.versions_listbox.insert(tk.END, ver)
        
        # Моды
        for item in self.mods_tree.get_children():
            self.mods_tree.delete(item)
        for mod in get_mods(self.minecraft_dir):
            status = "⚠️ ПОДОЗРИТЕЛЬНЫЙ" if mod['suspicious'] else "✅ Обычный"
            item = self.mods_tree.insert('', tk.END, values=(mod['name'], status, mod['path']))
            if mod['suspicious']:
                self.mods_tree.item(item, tags=('suspicious',))
        
        # Ресурспаки
        self.resp_listbox.delete(0, tk.END)
        for pack in get_resourcepacks(self.minecraft_dir):
            self.resp_listbox.insert(tk.END, pack)
        
        # DLL
        for item in self.dll_tree.get_children():
            self.dll_tree.delete(item)
        for dll in get_dll_files(self.minecraft_dir):
            status = "⚠️ ПОДОЗРИТЕЛЬНАЯ" if dll['suspicious'] else "✅ Обычная"
            item = self.dll_tree.insert('', tk.END, values=(dll['name'], status, dll['full_path']))
            if dll['suspicious']:
                self.dll_tree.item(item, tags=('suspicious',))
        
        # Папки
        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)
        for folder in get_suspicious_folders(self.minecraft_dir):
            item = self.folders_tree.insert('', tk.END, values=(folder['name'], folder['path']))
            if folder['suspicious']:
                self.folders_tree.item(item, tags=('suspicious',))
        
        # Инжект
        self.scan_injected()
        
        self.status_bar.config(text="Обновление завершено")

if __name__ == '__main__':
    root = tk.Tk()
    app = SCMScanner(root)
    root.mainloop()
