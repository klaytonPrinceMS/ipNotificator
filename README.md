# ipNotificator - IP Flutuante - Monitor de Rede

## Descrição
Overlay transparente que exibe o IP interno da rede em tempo real no canto inferior direito da tela. Perfeito para administradores de rede, desenvolvedores e técnicos.

## Características
- Sempre visível (mas não atrapalha)
- Fundo preto transparente (25% de opacidade)
- Texto branco centralizado com fonte Consolas
- Tamanho dinâmico - adapta ao IP (172.xxx.xxx.xxx)
- Auto-posicionamento - funciona em qualquer resolução
- Monitoramento automático de mudanças de IP/resolução
- Fechar: Duplo clique no texto
- Ultra leve: ~9 MB RAM, 0% CPU

## Consumo de Recursos
Memória RAM: 9 MB
CPU: 0%
Tamanho EXE: ~13 MB (PyInstaller)

## Requisitos
- Python 3.6+
- Tkinter (padrão do Python)
- Windows 10/11

## Instalação

### 1. Salvar Script
Salve como ip_flutuante.py

### 2. Executar Direto
python ip_flutuante.py

### 3. PyInstaller (Executável)
pip install pyinstaller
pyinstaller --onefile --noconsole --windowed ip_flutuante.py

## Configurações Personalizáveis
TRANSPARENCIA = 0.25    # 0.0 (invisível) a 1.0 (opaco)
HORIZONTAL = 110         # Distância da borda direita
VERTICAL = 60            # Distância da borda inferior

## Estrutura do Projeto
ip_flutuante/
├── ip_flutuante.py      # Script principal
├── README.md           # Este arquivo
└── dist/
    └── ip_flutuante.exe # Executável (após PyInstaller)

## Funcionalidades Técnicas
• Detecta IP interno (172.x.x.x preferencial)
• Fallback: socket.gethostbyname()
• Loop after(1000ms) - Zero CPU
• winfo_screenwidth/height auto-ajuste
• overrideredirect(True) - Sem bordas
• place(relx=0.5, rely=0.5) - Centralizado

## Posicionamento
Canto inferior direito:
┌─ 155px da direita ──┐
│                     │
│                 60px│ ← Distância da taskbar
│   [ 172.16.254.13 ] │
└─────────────────────┘

## Como Usar
1. Execute o script ou EXE
2. IP aparece no canto inferior direito
3. Duplo clique para fechar
4. Funciona 24/7 sem impacto no sistema

## Solução de Problemas
IP não aparece:
→ Verifique firewall/antivírus
→ Execute como administrador

Posição errada:
→ Ajuste HORIZONTAL/VERTICAL

Consumo muita RAM:
→ Normal: 9 MB é OTIMIZADO!

## Licença
MIT License - Uso livre para fins pessoais/commerciais
© 2026 - IP Flutuante Monitor

---
Status: RODANDO PERFEITO | 9 MB RAM | 0% CPU
