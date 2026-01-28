import tkinter as tk
from tkinter import messagebox
import socket
import os
import webbrowser
from datetime import datetime, timedelta
import json
import gc
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import random

# =================================================================
# CONFIGURAÇÕES GLOBAIS (ALTERE APENAS NESTA SEÇÃO)
# =================================================================
VERSAO = '1.3.20260121_v4'  # Versão com Alerta Visual de IP
COR_FUNDO = 'black'  # Cor de fundo do widget
COR_FONTE = 'white'  # Cor da fonte principal (IP e Datas)
COR_NEWS = '#ffffff'  # Cor do texto das notícias (Ticker)
COR_DESTAQUE_IP = 'cyan'  # Cor temporária ao copiar o IP
COR_ALERTA_IP = 'red'  # Cor do IP se estiver fora da faixa PREFIXO_REDE
COR_EASTER_EGG = 'gold'  # Cor do texto ao ativar o Easter Egg 42
COR_TITULO_EDITOR = '#FFD700'  # Cor do título no editor de datas
COR_BG_EDITOR = '#2b2b2b'  # Cor de fundo da janela do editor
COR_TXT_EDITOR = '#1e1e1e'  # Cor de fundo do campo de texto do editor
COR_BTN_SALVAR = '#28a745'  # Cor do botão salvar
COR_BTN_FECHAR = '#dc3545'  # Cor do botão fechar

TAMANHO_FONTE = 10  # Tamanho da fonte padrão
FONTE_PRINCIPAL = 'Consolas'  # Família da fonte para dados técnicos
FONTE_EMOJI = 'Segoe UI Emoji'  # Família da fonte para suporte a emojis

TRANSPARENCIA = 0.45  # Nível de transparência (0.0 a 1.0)
PREFIXO_REDE = '172.16'  # Prefixo do IP para filtrar a rede correta
POSICIONAR = False  # Se True, mantém o widget sempre no topo
CONFIG_FILE = 'ip_widget_datas.json'  # Nome do arquivo de datas personalizadas
CACHE_FILE = 'rss_cache.json'  # Nome do arquivo de cache das notícias
CACHE_DURATION = 28800  # Tempo de vida do cache RSS em segundos (8 horas)
RSS_RETRY_DELAY = 3600  # Intervalo mínimo de 1 hora entre tentativas de RSS (segundos)

# Configurações de Comportamento
UPDATE_MS_MONITOR = 15000  # Frequência de atualização do IP/Datas (ms)
TICKER_SPEED = 1.5  # Velocidade da animação do texto (pixels)
TICKER_ANIM_MS = 30  # Taxa de atualização da animação (ms)
TICKER_WAIT_MS = 0  # Tempo de espera antes de reiniciar o texto (ms)
NEWS_CYCLE_MS = 25000  # Tempo para trocar a notícia exibida (ms)
NEWS_LIMIT_PER_SOURCE = 10  # Quantidade de notícias por URL RSS
NEWS_TOTAL_LIMIT = 40  # Limite total de notícias no carrossel
TIMEOUT_CONEXAO = 8  # Tempo limite para conexão com RSS (segundos)
DEBUG_MODE = True  # Se False, silencia os logs de "Buscando..." no terminal
FILTRO_TEMPO = '7d'  # limite de tempo para pesquisas globais
FILTRO_LOCAL = '7d'  # limite de tempo para pesquisa de noticias locais

# RSS CONFIG - ESTRUTURA DICONÁRIO (NOVO)
RSS_URLS = {
    #"Monte Santo": f"https://news.google.com/rss/search?q=%22Monte+Santo+de+Minas%22+when:{FILTRO_LOCAL}&hl=pt-BR&gl=BR&ceid=BR:pt-419", #por ter poucas noticias o RSS, bloqueia o acesso do sistema
    #"Região/MSM": f"https://news.google.com/rss/search?q=Prefeitura+OR+Câmara+Monte+Santo+de+Minas+when:{FILTRO_LOCAL}&hl=pt-BR&gl=BR&ceid=BR:pt-419", #por ter poucas noticias o RSS, bloqueia o acesso do sistema
    "Ciberataques": f"https://news.google.com/rss/search?q=ciberataque+OR+ransomware+Brasil+when:{FILTRO_TEMPO}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Tecnologia/TI": f"https://news.google.com/rss/search?q=%22segurança+da+informação%22+OR+tecnologia+when:{FILTRO_TEMPO}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Segurança/Vazamentos": f"https://news.google.com/rss/search?q=vazamento+dados+OR+vulnerabilidade+when:{FILTRO_TEMPO}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
}

# Calendario GLOBAL, mesmo apagando no EDITAR, ainda permanece no sistema
DATAS_PADRAO = {
    "06-01": {"emoji": "🎊", "frase": "Feliz Ano Novo"},
    "13-09": {"emoji": "🧑🏽‍💻", "frase": "import antigravity", "easter": True},
    "25-12": {"emoji": "🎅🎄", "frase": "Feliz Natal"},
}

# VARIÁVEIS GLOBAIS CACHE (CORRIGIDO - INCLUI _rss_last_error)
_datas_cache = None
_datas_cache_data = None
_rss_cache = []
_rss_cache_timestamp = 0
_current_news_index = 0
_rss_last_error = 0  # Timestamp do último erro RSS completo (CORREÇÃO DO ERRO)


# =================================================================
# CLASSES E FUNÇÕES
# =================================================================

class NewsTicker(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, height=25, bg=COR_FUNDO, highlightthickness=0)
        self.text = ""
        self.text_id = None
        self.pos_x = 0
        self.anim_id = None
        self.speed = TICKER_SPEED
        self.canvas_width = 300

    def set_news(self, text):
        """Define uma nova notícia e inicia a posição na direita"""
        if self.anim_id:
            self.after_cancel(self.anim_id)

        self.text = text
        self.update_canvas_width()
        self.pos_x = self.canvas_width + 10
        self.animate()

    def update_canvas_width(self):
        self.canvas_width = max(self.winfo_width(), 200)

    def animate(self):
        self.delete("all")
        self.update_canvas_width()

        if self.text:
            # Criamos o texto e pegamos o ID para medir
            self.text_id = self.create_text(self.pos_x, 13, text=self.text,
                                            fill=COR_NEWS, font=(FONTE_PRINCIPAL, 10, 'bold'),
                                            anchor='w', tags='ticker')

            # Medimos a largura real do texto no Canvas
            bbox = self.bbox(self.text_id)
            text_width = bbox[2] - bbox[0] if bbox else len(self.text) * 8
        else:
            text_width = 0

        # Move para a esquerda
        self.pos_x -= self.speed

        # Se o FINAL do texto (pos_x + largura) sumiu pela esquerda (0)
        if self.pos_x + text_width < 0:
            # Carrega a próxima notícia IMEDIATAMENTE
            self.text = get_proxima_noticia()
            self.pos_x = self.canvas_width + 10
            self.anim_id = self.after(TICKER_ANIM_MS, self.animate)
        else:
            # Continua a animação da notícia atual
            self.anim_id = self.after(TICKER_ANIM_MS, self.animate)

    def start_news_cycle(self):
        """Inicia apenas a primeira notícia. O loop agora é controlado pelo fim do texto no animate()"""
        news_text = get_proxima_noticia()
        self.set_news(news_text)


def calcular_tempo_atras(data_string):
    """Converte datas do RSS em formato amigável (ex: 3h atrás) sem Warnings"""
    if not data_string:
        return ""
    try:
        # Formato do Google News: Wed, 21 Jan 2026 15:30:00 GMT
        formato = "%a, %d %b %Y %H:%M:%S"
        data_limpa = " ".join(data_string.split()[:5])

        # Converte para objeto datetime
        data_noticia = datetime.strptime(data_limpa, formato)

        # NOVA FORMA (Python 3.12+): Evita o DeprecationWarning
        from datetime import timezone
        agora = datetime.now(timezone.utc).replace(tzinfo=None)

        diferenca = agora - data_noticia

        if diferenca.days > 0:
            return f"{diferenca.days}d atrás"

        segundos = diferenca.total_seconds()
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)

        if horas > 0:
            return f"{horas}h atrás"
        if minutos > 0:
            return f"{minutos}min atrás"
        return "agora"
    except:
        return ""


def safe_text(text):
    """Limpa o texto e remove o limite de caracteres (...)"""
    if not text:
        return "Notícia sem título"
    try:
        # Remove apenas espaços extras, sem cortar o tamanho
        clean_text = str(text).strip()
        # Opcional: remove o nome da fonte que o Google às vezes repete no título
        if " - " in clean_text:
            clean_text = clean_text.rsplit(" - ", 1)[0]
        return clean_text
    except:
        return "Erro ao processar texto"


def carregar_rss_multiplas_fontes():
    """Carrega RSS com retry inteligente de 1h e estrutura dicionário"""
    global _rss_cache, _rss_cache_timestamp, _current_news_index, _rss_last_error
    agora = time.time()

    # Cache OK: usa cache existente
    if _rss_cache and agora - _rss_cache_timestamp < CACHE_DURATION:
        return _rss_cache

    # SEM NOTÍCIAS + ERRO RECENTE (última hora): NÃO TENTA
    if _rss_last_error and agora - _rss_last_error < RSS_RETRY_DELAY:
        if DEBUG_MODE:
            print(f"⏳ RSS aguardando {int((RSS_RETRY_DELAY - (agora - _rss_last_error)) // 60)}min para retry...")
        return []

    # Tenta carregar
    todas_noticias = set()
    erro_atual = False

    for nome_exibicao, url in RSS_URLS.items():
        try:
            i = len(todas_noticias) + 1
            url_safe = urllib.parse.quote(url, safe=':/?&=')

            if DEBUG_MODE:
                print(f"🔄 Fonte {i}/{len(RSS_URLS)} ({nome_exibicao}): Buscando...")

            req = urllib.request.Request(url_safe, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT_CONEXAO) as response:
                xml_content = response.read().decode('utf-8', errors='replace')

            root = ET.fromstring(xml_content.encode('utf-8'))
            items = root.findall('.//item')[:NEWS_LIMIT_PER_SOURCE]

            for item in items:
                title_elem = item.find('title')
                date_elem = item.find('pubDate')

                if title_elem is not None and title_elem.text:
                    titulo = safe_text(title_elem.text)
                    tempo_atras = ""
                    if date_elem is not None:
                        tempo_atras = calcular_tempo_atras(date_elem.text)
                    data_display = f" ({tempo_atras})" if tempo_atras else ""
                    todas_noticias.add(f"📰 {titulo}{data_display} [{nome_exibicao}]")

        except Exception as e:
            erro_atual = True
            print(f"❌ Erro na fonte '{nome_exibicao}': {str(e)}")
            continue

    # REGISTRA ERRO ou SUCESSO
    if erro_atual and not todas_noticias:
        _rss_last_error = agora
        print("❌ Todas as fontes falharam. Aguardando 1h para próximo retry.")
        return []

    # Sucesso
    lista_final = list(todas_noticias)
    random.shuffle(lista_final)
    _rss_cache = lista_final[:NEWS_TOTAL_LIMIT]
    _rss_cache_timestamp = agora
    _current_news_index = 0
    _rss_last_error = 0

    print(f"✅ {len(_rss_cache)} notícias únicas carregadas!")
    return _rss_cache


def get_proxima_noticia():
    global _current_news_index
    noticias = carregar_rss_multiplas_fontes()
    if not noticias:
        return None  # Retorna None em vez de mensagem (corrigido)

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
                    else:
                        get_internal_ip_cache.cache = ip_teste
                except:
                    get_internal_ip_cache.cache = 'Erro ao Localizar'
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
                                          font=(FONTE_EMOJI, TAMANHO_FONTE),
                                          fg=COR_FONTE, bg=COR_FUNDO)
        self.label_comemoracao.pack()

        self.label_ip = tk.Label(self.frame, text="Iniciando...",
                                 font=(FONTE_PRINCIPAL, TAMANHO_FONTE, 'bold'),
                                 fg=COR_FONTE, bg=COR_FUNDO)
        self.label_ip.pack()

        self.ticker = NewsTicker(self.frame)
        self.ticker.pack(fill='x', pady=(5, 0))

        for widget in [self.label_ip, self.label_comemoracao, self.ticker, self.frame]:
            widget.bind('<Triple-Button-1>', self.fechar)
            widget.bind('<Button-1>', self.clique_esquerdo)
            widget.bind('<Button-3>', self.menu_contexto)

        self.criar_menu()
        self.verificar_atualizacoes()

    def agendar_monitoramento(self):
        if self.monitor_id:
            self.root.after_cancel(self.monitor_id)
        if not self.root.winfo_viewable():
            return
        self.monitor_id = self.root.after(UPDATE_MS_MONITOR, self.verificar_atualizacoes)

    def verificar_atualizacoes(self):
        self.monitor_id = None
        ip_novo = get_internal_ip_cache()
        res_novo = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        com_novo = get_data_hoje_otimizada()

        cor_ip = COR_FONTE
        if ip_novo and not ip_novo.startswith(PREFIXO_REDE) and "Erro" not in ip_novo:
            cor_ip = COR_ALERTA_IP

        mudou = (ip_novo != self.ip_atual or
                 res_novo != self.res_atual or
                 com_novo != self.comemoracao_atual)

        if mudou:
            self.ip_atual = ip_novo
            self.res_atual = res_novo
            self.comemoracao_atual = com_novo
            self.label_ip.config(text=ip_novo, fg=cor_ip)

            if com_novo:
                # Tem data comemorativa: esconde ticker
                self.label_comemoracao.config(text=f"{com_novo['emoji']} {com_novo['frase']}")
                self.label_comemoracao.pack(pady=2)
                self.ticker.pack_forget()
            else:
                # Sem data: verifica notícias antes de mostrar ticker
                self.label_comemoracao.pack_forget()
                noticias = carregar_rss_multiplas_fontes()
                if noticias:  # SÓ mostra ticker SE tiver notícias
                    self.ticker.pack(fill='x', pady=(5, 0))
                    if not self.ticker.text:
                        self.ticker.start_news_cycle()
                else:
                    # SEM notícias: esconde ticker, mostra só IP
                    self.ticker.pack_forget()

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
            altura = 75

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
            cor_original = self.label_ip['fg']
            self.label_ip.config(text="🏆 EASTER EGG 42! 🏆", fg=COR_EASTER_EGG,
                                 font=(FONTE_PRINCIPAL, TAMANHO_FONTE + 2, 'bold'))
            self.root.after(3000, lambda: self.label_ip.config(
                text=self.ip_atual, fg=cor_original, font=(FONTE_PRINCIPAL, TAMANHO_FONTE, 'bold')))

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
            cor_antiga = self.label_ip['fg']
            self.label_ip.config(fg=COR_DESTAQUE_IP)
            self.root.after(300, lambda: self.label_ip.config(fg=cor_antiga))

    def atualizar(self):
        carregar_datas_otimizado()
        self.verificar_atualizacoes()

    def atualizar_rss(self):
        global _rss_cache_timestamp, _current_news_index, _rss_last_error
        _rss_cache_timestamp = 0
        _current_news_index = 0
        _rss_last_error = 0
        if hasattr(self, 'ticker'):
            self.ticker.start_news_cycle()

    def editor_datas(self):
        editor = tk.Toplevel(self.root)
        editor.title(f"DTI - PMMSM          {VERSAO}")
        editor.geometry("600x500")
        editor.configure(bg=COR_BG_EDITOR)
        editor.transient(self.root)
        editor.grab_set()

        tk.Label(editor, text="DD-MM | emoji frase\nEx: 20-01 | 🎉 Hoje!",
                 bg=COR_BG_EDITOR, fg=COR_TITULO_EDITOR, font=(FONTE_PRINCIPAL, 10)).pack(pady=10)

        frame_txt = tk.Frame(editor, bg=COR_BG_EDITOR)
        frame_txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        sb = tk.Scrollbar(frame_txt)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt = tk.Text(frame_txt, bg=COR_TXT_EDITOR, fg=COR_FONTE, font=(FONTE_PRINCIPAL, 10),
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

        tk.Button(editor, text="💾 SALVAR", command=salvar, bg=COR_BTN_SALVAR, fg=COR_FONTE,
                  font=(FONTE_PRINCIPAL, 11, 'bold'), height=2, width=12).pack(pady=10)
        tk.Button(editor, text="❌ Fechar", command=editor.destroy,
                  bg=COR_BTN_FECHAR, fg=COR_FONTE, font=(FONTE_PRINCIPAL, 11, 'bold'),
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
