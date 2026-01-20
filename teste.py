import tkinter as tk
from tkinter import messagebox
import socket
import os
import webbrowser
from datetime import datetime
import json
import gc

# Configurações
TRANSPARENCIA = 0.45
VERSAO = '1.5.20260120-FIXED'
COR_FUNDO = 'black'
COR_FONTE = 'white'
TAMANHO_FONTE = 10
PREFIXO_REDE = '172.16'
CONFIG_FILE = 'ip_widget_datas.json'

# Datas Padrão (Imutáveis)
DATAS_PADRAO = {
    "06-01": {"emoji": "🎊", "frase": "Feliz Ano Novo"},
    "13-09": {"emoji": "🧑🏽‍💻", "frase": "import antigravity"},
    "25-12": {"emoji": "🎅🎄", "frase": "Feliz Natal"},
}


class DataManager:
    """Gerencia datas com cache e persistência."""
    _cache = None
    _last_mod = 0

    @classmethod
    def carregar(cls):
        try:
            if os.path.exists(CONFIG_FILE):
                mtime = os.path.getmtime(CONFIG_FILE)
                if mtime > cls._last_mod:
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        custom = json.load(f)
                    cls._cache = {**DATAS_PADRAO, **custom}
                    cls._last_mod = mtime
            elif cls._cache is None:
                cls._cache = DATAS_PADRAO.copy()
        except Exception:
            cls._cache = DATAS_PADRAO.copy()
        return cls._cache

    @classmethod
    def salvar(cls, dados):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            cls._last_mod = 0  # Força recarregamento no próximo 'carregar'
            cls._cache = None
            return True
        except Exception:
            return False


def get_ip_eficiente():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.1)
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            return ip if ip.startswith(PREFIXO_REDE) else f"IP: {ip}"
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Erro de Rede"


class IPWidget:
    def __init__(self, root):
        self.root = root
        self.ip_atual = ""
        self.com_atual = None

        root.attributes('-topmost', True)
        root.attributes('-alpha', TRANSPARENCIA)
        root.overrideredirect(True)
        root.configure(bg=COR_FUNDO)

        self.label_com = tk.Label(root, text="", font=('Segoe UI Emoji', TAMANHO_FONTE), fg=COR_FONTE, bg=COR_FUNDO)
        self.label_ip = tk.Label(root, text="...", font=('Consolas', TAMANHO_FONTE, 'bold'), fg=COR_FONTE, bg=COR_FUNDO)

        for w in (root, self.label_com, self.label_ip):
            w.bind('<Triple-Button-1>', lambda e: root.destroy())
            w.bind('<Button-3>', self.mostrar_menu)
            w.bind('<Button-1>', self.copiar_ip)

        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Copiar IP", command=self.copiar_ip)
        self.menu.add_command(label="Editar Datas", command=self.abrir_editor)
        self.menu.add_separator()
        self.menu.add_command(label="Sair", command=root.destroy)

        self.atualizar_ciclo()

    def atualizar_ciclo(self):
        ip = get_ip_eficiente()
        datas = DataManager.carregar()
        hoje_str = datetime.now().strftime("%d-%m")
        com = datas.get(hoje_str)

        if ip != self.ip_atual or com != self.com_atual:
            self.ip_atual = ip
            self.com_atual = com
            self.label_ip.config(text=ip)

            if com:
                self.label_com.config(text=f"{com['emoji']} {com['frase']}")
                self.label_com.pack(side="top", pady=(2, 0))
            else:
                self.label_com.pack_forget()

            self.label_ip.pack(side="top", padx=5, pady=2)
            self.ajustar_posicao()
            gc.collect()

        self.root.after(30000, self.atualizar_ciclo)

    def ajustar_posicao(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{sw - w - 10}+{sh - h - 50}")

    def mostrar_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def copiar_ip(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ip_atual)
        self.label_ip.config(fg='cyan')
        self.root.after(500, lambda: self.label_ip.config(fg=COR_FONTE))

    def abrir_editor(self):
        editor = tk.Toplevel(self.root)
        editor.title("Editor de Datas")
        editor.geometry("450x400")
        editor.attributes('-topmost', True)

        tk.Label(editor, text="Formato: DD-MM | Emoji Frase", font=('Arial', 9, 'bold')).pack(pady=5)

        txt = tk.Text(editor, font=('Consolas', 10), undo=True)
        txt.pack(fill="both", expand=True, padx=10, pady=5)

        # Carrega apenas as datas customizadas para edição
        datas_completas = DataManager.carregar()
        custom_data = {k: v for k, v in datas_completas.items() if k not in DATAS_PADRAO or DATAS_PADRAO[k] != v}

        content = ""
        for k, v in sorted(datas_completas.items()):
            content += f"{k} | {v['emoji']} {v['frase']}\n"
        txt.insert("1.0", content.strip())

        def salvar():
            novas_custom = {}
            linhas = txt.get("1.0", "end-1c").split("\n")
            for line in linhas:
                if "|" in line:
                    try:
                        parts = line.split("|")
                        data_key = parts[0].strip()
                        resto = parts[1].strip().split(maxsplit=1)
                        if len(resto) >= 2:
                            emoji, frase = resto[0], resto[1]
                            # Só salva se for diferente do padrão
                            if data_key not in DATAS_PADRAO or DATAS_PADRAO[data_key]['emoji'] != emoji or \
                                    DATAS_PADRAO[data_key]['frase'] != frase:
                                novas_custom[data_key] = {"emoji": emoji, "frase": frase}
                    except:
                        continue

            if DataManager.salvar(novas_custom):
                messagebox.showinfo("Sucesso", "Datas salvas com sucesso!")
                editor.destroy()
                self.atualizar_ciclo()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o arquivo.")

        btn_frame = tk.Frame(editor)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Cancelar", command=editor.destroy, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Salvar", command=salvar, bg="#28a745", fg="white", width=10).pack(side="left",
                                                                                                     padx=5)


if __name__ == "__main__":
    if os.name == 'nt':
        try:
            import ctypes

            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

    root = tk.Tk()
    app = IPWidget(root)
    root.mainloop()
