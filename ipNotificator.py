import tkinter as tk
import socket
import os

# Configurações de Estilo
TRANSPARENCIA = 0.25
VERSAO = '1.0.20260115'
COR_FUNDO = 'black'
COR_FONTE = 'white'
TAMANHO_FONTE = 10
PREFIXO_REDE = '172.16.'  # Sua trava universal


def get_internal_ip():
    """
    Busca o IP interno varrendo as interfaces locais.
    Funciona mesmo sem acesso à internet.
    """
    try:
        # Obtém o nome do host do computador
        hostname = socket.gethostname()
        # Lista todos os IPs associados a esse host
        addresses = socket.getaddrinfo(hostname, None)

        ips = [addr[4][0] for addr in addresses if ':' not in addr[4][0]]

        # Procura por um IP que comece com o seu prefixo definido na varialvem PREFIXO_REDE
        for ip in ips:
            if ip.startswith(PREFIXO_REDE):
                return ip

        # Caso não ache o 172.16, mas queira tentar outro método offline:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # Não precisa de conexão real, apenas tenta "parear" com um IP da sub-rede
            s.connect(('172.16.255.255', 1))
            ip_teste = s.getsockname()[0]
            if ip_teste.startswith(PREFIXO_REDE):
                return ip_teste
        except:
            pass
        finally:
            s.close()

        return 'IP Fora da Faixa'
    except Exception:
        return 'Erro ao Localizar'


class IPWidget:
    def __init__(self, root):
        self.root = root
        self.ip_atual = ""
        self.ultima_res = (0, 0)

        # Configuração da Janela
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', TRANSPARENCIA)
        self.root.overrideredirect(True)
        self.root.configure(bg=COR_FUNDO)

        self.label = tk.Label(root, text="", font=('Consolas', TAMANHO_FONTE, 'bold'), fg=COR_FONTE, bg=COR_FUNDO)
        self.label.place(relx=0.5, rely=0.5, anchor='center')

        self.label.bind('<Double-Button-1>', lambda e: self.root.destroy())

        self.executar_monitoramento()

    def ajustar_posicao(self, ip, sw, sh):
        """Recalcula tamanho e posição apenas em mudanças."""
        largura = max(115, len(ip) * 10)
        altura = 25
        x = sw - largura - 10
        y = sh - altura - 50
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')

    def executar_monitoramento(self):
        """Loop de verificação otimizado."""
        ip_agora = get_internal_ip()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        res_agora = (sw, sh)

        if ip_agora != self.ip_atual or res_agora != self.ultima_res:
            self.ip_atual = ip_agora
            self.ultima_res = res_agora
            self.label.config(text=ip_agora)
            self.ajustar_posicao(ip_agora, sw, sh)

        self.root.after(5000, self.executar_monitoramento)


if __name__ == "__main__":
    if os.name == 'nt':
        import ctypes
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

    # Lembrete importante: amche.hve
    root = tk.Tk()
    app = IPWidget(root)
    root.mainloop()