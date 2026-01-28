import tkinter as tk
from tkinter import messagebox
import socket
import os
import webbrowser
from datetime import datetime, timedelta
import json
import gc
import urllib.request
import xml.etree.ElementTree as ET
import time

# Configurações ULTRA OTIMIZADAS
TRANSPARENCIA = 0.45
VERSAO = '1.3.20260120'
COR_FUNDO = 'black'
COR_FONTE = 'white'
TAMANHO_FONTE = 10
PREFIXO_REDE = '172.16'
POSICIONAR = False
CONFIG_FILE = 'ip_widget_datas.json'

# RSS CONFIG
RSS_URL = "https://news.google.com/rss/search?q=ataque+hacker+prefeitura+OR+invas%C3%A3o+sistemas+prefeitura+Brasil+when:7d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
CACHE_FILE = 'rss_cache.json'
CACHE_DURATION = 1800  # 30 minutos

# CACHE GLOBAL
DATAS_PADRAO = {
    "06-01": {"emoji": "🎊", "frase": "Feliz Ano Novo"},
    "13-09": {"emoji": "🧑🏽‍💻", "frase": "import antigravity", "easter": True},
    "25-12": {"emoji": "🎅🎄", "frase": "Feliz Natal"},
}

_datas_cache = None
_datas_cache_data = None
_rss_cache = []
_rss_cache_timestamp = 0
_current_news_index = 0


class NewsTicker(tk.Canvas):
    """Ticker FLUIDO da esquerda para a direita com tempo de leitura"""

    def __init__(self, parent):
        # ✅ CORRIGIDO: Removeu **kwargs conflitante
        super().__init__(parent, height=25, bg=COR_FUNDO, highlightthickness=0)
        self.text = ""
        self.text_id = None
        self.pos_x = 0
        self.anim_id = None
        self.news_cycle_id = None
        self.speed = 2
        self.wait_time = 3000  # 3s pausa para leitura
        self.canvas_width = 300  # Largura estimada inicial

    def set_news(self, text):
        """Define nova notícia e reinicia animação"""
        self.text = text
        self.pos_x = self.canvas_width + 50  # Começa fora da tela (direita)
        self.start_animation()

    def start_animation(self):
        """Inicia animação fluida"""
        if self.anim_id:
            self.after_cancel(self.anim_id)

        self.delete("all")
        if self.text:
            self.text_id = self.create_text(self.pos_x, 13, text=self.text,
                                            fill='#00ff00', font=('Consolas', 10, 'bold'),
                                            anchor='w', tags='ticker')
        self.update_canvas_width()
        self.animate()

    def update_canvas_width(self):
        """Atualiza largura do canvas"""
        self.canvas_width = max(self.winfo_width(), 200)

    def animate(self):
        """Animação contínua L→R fluida"""
        self.delete("all")
        self.update_canvas_width()

        if self.text:
            self.create_text(self.pos_x, 13, text=self.text,
                             fill='#00ff00', font=('Consolas', 10, 'bold'),
                             anchor='w', tags='ticker')

        # Move para esquerda
        self.pos_x -= self.speed

        # Se saiu completamente da tela, pausa para leitura
        text_width = len(self.text) * 8
        if self.pos_x < -text_width - 20:
            # Pausa 3s para leitura completa
            self.after(self.wait_time, self.reset_position)
        else:
            # Continua animação fluida (50ms = ~60fps)
            self.anim_id = self.after(50, self.animate)

    def reset_position(self):
        """Reseta posição para próxima iteração"""
        self.pos_x = self.canvas_width + 50
        self.anim_id = self.after(50, self.animate)

    def start_news_cycle(self):
        """Ciclo de notícias - nova a cada 25s"""
        if self.news_cycle_id:
            self.after_cancel(self.news_cycle_id)

        def cycle():
            news_text = get_proxima_noticia()
            self.set_news(news_text)
            self.news_cycle_id = self.after(25000, cycle)

        cycle()


def carregar_rss_simples():
    """RSS simples SEM dependências externas"""
    global _rss_cache, _rss_cache_timestamp, _current_news_index

    agora = time.time()
    if agora - _rss_cache_timestamp < CACHE_DURATION and _rss_cache:
        return _rss_cache

    try:
        with urllib.request.urlopen(RSS_URL, timeout=10) as response:
            xml_content = response.read().decode('utf-8')

        root = ET.fromstring(xml_content)
        noticias = []

        for item in root.findall('.//item'):
            title_elem = item.find('title')
            pubdate_elem = item.find('pubDate')

            if title_elem is not None and title_elem.text:
                titulo = title_elem.text.strip()
                data = "Data não disponível"

                if pubdate_elem is not None and pubdate_elem.text:
                    data_raw = pubdate_elem.text
                    data = data_raw[:16] if len(data_raw) > 16 else data_raw

                noticias.append(f"📰 {titulo} | {data}")

        _rss_cache = noticias[:8]
        _rss_cache_timestamp = agora
        _current_news_index = 0

        cache_data = {'noticias': _rss_cache, 'timestamp': agora}
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
        except:
            pass

    except Exception as e:
        print(f"Erro RSS: {e}")
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if agora - cache_data['timestamp'] < CACHE_DURATION * 2:
                        _rss_cache = cache_data['noticias']
        except:
            _rss_cache = ["📰 Aguardando notícias de cibersegurança..."]

    return _rss_cache


def get_proxima_noticia():
    """Rotaciona notícias"""
    global _current_news_index
    noticias = carregar_rss_simples()
    if not noticias:
        return "📰 Carregando notícias..."

    noticia = noticias[_current_news_index]
    _current_news_index = (_current_news_index + 1) % len(noticias)
    return noticia


def carregar_datas_otimizado():
    global _datas_cache, _datas_cache_data
    try:
        if os.path.exists(CONFIG_FILE):
            mod_time = os.path.getmtime(CONFIG_FILE)
            if _datas_cache_data != mod_time:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    custom = json.load(f)
                _datas_cache = {**DATAS_PADRAO, **custom}
                _datas_cache_data = mod_time
                gc.collect()
        else:
            _datas_cache = DATAS_PADRAO
    except:
        _datas_cache = DATAS_PADRAO
    return _datas_cache


def salvar_datas_personalizadas(datas):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(datas, f, indent=2, ensure_ascii=False)
        gc.collect()
        return True
    except:
        return False


def get_data_hoje_otimizada():
    global _datas_cache
    if _datas_cache is None:
        carregar_datas_otimizado()

    hoje = datetime.now()
    dia_hoje = hoje.day
    mes_hoje = hoje.month

    data_key = f"{dia_hoje:02d}-{mes_hoje:02d}"
    if data_key in _datas_cache:
        return _datas_cache[data_key]

    for data_key, info in _datas_cache.items():
        try:
            dia, mes = map(int, data_key.split("-"))
            data_com = datetime(hoje.year, mes, dia)
            inicio = data_com - timedelta(days=7)
            fim = data_com + timedelta(days=1)
            if inicio <= hoje <= fim:
                return info
        except:
            continue
    return None


def get_internal_ip_cache():
    if not hasattr(get_internal_ip_cache, "cache"):
        get_internal_ip_cache.cache = None
        get_internal_ip_cache.timestamp = 0

    agora = datetime.now().timestamp()
    if agora - get_internal_ip_cache.timestamp > 30:
        try:
            hostname = socket.gethostname()
            addresses = socket.getaddrinfo(hostname, None)
            ips = [addr[4][0] for addr in addresses if ':' not in addr[4][0]]
            for ip in ips:
                if ip.startswith(PREFIXO_REDE):
                    get_internal_ip_cache.cache = ip
                    break
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0.1)
                try:
                    s.connect(('192.168.255.255', 1))
                    ip_teste = s.getsockname()[0]
                    if ip_teste.startswith(PREFIXO_REDE):
                        get_internal_ip_cache.cache = ip_teste
                except:
                    get_internal_ip_cache.cache = 'IP Fora da Faixa'
                finally:
                    s.close()
        except:
            get_internal_ip_cache.cache = 'Erro ao Localizar'
        get_internal_ip_cache.timestamp = agora
    return get_internal_ip_cache.cache


class IPWidget:
    def __init__(self, root):
        self.root = root
        self.ip_atual = ""
        self.res_atual = (0, 0)
        self.comemoracao_atual = None
        self.click_count = 0
        self.last_click = 0
        self.easter42 = False
        self.monitor_id = None

        self.root.attributes('-topmost', POSICIONAR)
        self.root.attributes('-alpha', TRANSPARENCIA)
        self.root.overrideredirect(True)
        self.root.configure(bg=COR_FUNDO)
        self.root.update_idletasks()

        self.frame = tk.Frame(root, bg=COR_FUNDO)
        self.frame.pack(padx=5, pady=3)

        self.label_comemoracao = tk.Label(self.frame, text="",
                                          font=('Segoe UI Emoji', TAMANHO_FONTE),
                                          fg=COR_FONTE, bg=COR_FUNDO)
        self.label_comemoracao.pack()

        self.label_ip = tk.Label(self.frame, text="Iniciando...",
                                 font=('Consolas', TAMANHO_FONTE, 'bold'),
                                 fg=COR_FONTE, bg=COR_FUNDO)
        self.label_ip.pack()

        # ✅ TICKER CORRIGIDO
        self.ticker = NewsTicker(self.frame)
        self.ticker.pack(fill='x', pady=(5, 0))

        for widget in [self.label_ip, self.label_comemoracao, self.ticker, self.frame]:
            widget.bind('<Triple-Button-1>', self.fechar)
            widget.bind('<Button-1>', self.clique_esquerdo)
            widget.bind('<Button-3>', self.menu_contexto)

        self.criar_menu()
        self.verificar_atualizacoes()
        self.ticker.start_news_cycle()

    def agendar_monitoramento(self):
        if self.monitor_id:
            self.root.after_cancel(self.monitor_id)
        if not self.root.winfo_viewable():
            return
        self.monitor_id = self.root.after(15000, self.verificar_atualizacoes)

    def verificar_atualizacoes(self):
        self.monitor_id = None
        ip_novo = get_internal_ip_cache()
        res_novo = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        com_novo = get_data_hoje_otimizada()

        mudou = (ip_novo != self.ip_atual or
                 res_novo != self.res_atual or
                 com_novo != self.comemoracao_atual)

        if mudou:
            self.ip_atual = ip_novo
            self.res_atual = res_novo
            self.comemoracao_atual = com_novo
            self.label_ip.config(text=ip_novo)

            if com_novo:
                self.label_comemoracao.config(text=f"{com_novo['emoji']} {com_novo['frase']}")
                self.label_comemoracao.pack(pady=2)
                self.ticker.pack_forget()
            else:
                self.label_comemoracao.pack_forget()
                self.ticker.pack(fill='x', pady=(5, 0))
                self.ticker.start_news_cycle()

            self.redimensionar()

        self.agendar_monitoramento()
        gc.collect()

    def redimensionar(self):
        largura_ip = max(115, len(self.ip_atual) * 10)
        if self.comemoracao_atual:
            larg_com = len(f"{self.comemoracao_atual['emoji']} {self.comemoracao_atual['frase']}") * 9
            largura = max(largura_ip, larg_com) + 20
            altura = 55
        else:
            largura = largura_ip + 20
            altura = 75  # + ticker

        sw, sh = self.res_atual
        x = sw - largura - 10
        y = sh - altura - 50
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')

    def fechar(self, event):
        if self.monitor_id:
            self.root.after_cancel(self.monitor_id)
        self.root.destroy()

    def clique_esquerdo(self, event):
        agora = datetime.now()
        if (agora - datetime.fromtimestamp(self.last_click)).total_seconds() > 2:
            self.click_count = 0
        self.click_count += 1
        self.last_click = agora.timestamp()
        if self.click_count == 42 and not self.easter42:
            self.easter42 = True
            cor = self.label_ip['fg']
            self.label_ip.config(text="🏆 EASTER EGG 42! 🏆", fg='gold',
                                 font=('Consolas', TAMANHO_FONTE + 2, 'bold'))
            self.root.after(3000, lambda: self.label_ip.config(
                text=self.ip_atual, fg=cor, font=('Consolas', TAMANHO_FONTE, 'bold')))

    def criar_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Copiar IP", command=self.copiar_ip)
        self.menu.add_command(label="Atualizar", command=self.atualizar)
        self.menu.add_separator()
        self.menu.add_command(label="Editar Datas", command=self.editor_datas)
        self.menu.add_command(label="🔄 Atualizar Notícias", command=self.atualizar_rss)

    def menu_contexto(self, event):
        com = get_data_hoje_otimizada()
        if com and "antigravity" in com.get('frase', ''):
            try:
                webbrowser.open('https://mrdoob.com/projects/chromeexperiments/google-gravity/')
                self.label_ip.config(text="🛸 Antigravidade!")
                self.root.after(2000, lambda: self.label_ip.config(text=self.ip_atual))
            except:
                pass
        else:
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def copiar_ip(self):
        if self.ip_atual and 'Erro' not in self.ip_atual:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.ip_atual)
            self.label_ip.config(fg='cyan')
            self.root.after(300, lambda: self.label_ip.config(fg=COR_FONTE))

    def atualizar(self):
        carregar_datas_otimizado()
        self.verificar_atualizacoes()

    def atualizar_rss(self):
        global _rss_cache_timestamp, _current_news_index
        _rss_cache_timestamp = 0
        _current_news_index = 0
        if hasattr(self, 'ticker'):
            self.ticker.start_news_cycle()

    def editor_datas(self):
        editor = tk.Toplevel(self.root)
        editor.title(f"DTI - PMMSM          {VERSAO}")
        editor.geometry("600x500")
        editor.configure(bg='#2b2b2b')
        editor.transient(self.root)
        editor.grab_set()

        tk.Label(editor, text="DD-MM | emoji frase\nEx: 20-01 | 🎉 Hoje!",
                 bg='#2b2b2b', fg='#FFD700', font=('Consolas', 10)).pack(pady=10)

        frame_txt = tk.Frame(editor, bg='#2b2b2b')
        frame_txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        sb = tk.Scrollbar(frame_txt)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt = tk.Text(frame_txt, bg='#1e1e1e', fg='white', font=('Consolas', 10),
                      yscrollcommand=sb.set, wrap=tk.WORD, height=16)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)

        datas = carregar_datas_otimizado()
        txt.delete("1.0", tk.END)
        for data, info in sorted(datas.items()):
            txt.insert(tk.END, f"{data} | {info['emoji']} {info['frase']}\n")

        def salvar():
            novas = {}
            for linha in txt.get("1.0", tk.END).strip().split('\n'):
                if '|' in linha:
                    data, resto = linha.split('|', 1)
                    data, resto = data.strip(), resto.strip()
                    partes = resto.split(maxsplit=1)
                    emoji = partes[0] if partes else "🎉"
                    frase = partes[1] if len(partes) > 1 else "Evento"
                    novas[data] = {"emoji": emoji, "frase": frase}

            if salvar_datas_personalizadas(novas):
                editor.destroy()
                self.atualizar()
                messagebox.showinfo("✅", f"Salvas {len(novas)} datas!")
            else:
                messagebox.showerror("❌", "Erro ao salvar")

        tk.Button(editor, text="💾 SALVAR", command=salvar, bg='#28a745', fg='white',
                  font=('Consolas', 11, 'bold'), height=2, width=12).pack(pady=10)
        tk.Button(editor, text="❌ Fechar", command=editor.destroy,
                  bg='#dc3545', fg='white', font=('Consolas', 11, 'bold'),
                  height=2, width=12).pack(pady=5)


if __name__ == "__main__":
    if os.name == 'nt':
        import ctypes

        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

    gc.collect()
    root = tk.Tk()
    app = IPWidget(root)
    root.mainloop()
    gc.collect()
