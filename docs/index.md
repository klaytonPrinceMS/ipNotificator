# ipNotificator - IP Flutuante - Monitor de Rede

## Descrição
Overlay transparente que exibe o IP interno da rede em tempo real no canto inferior direito da tela. Perfeito para administradores de rede, desenvolvedores e técnicos.

## Características
- Sempre visível (mas não atrapalha)
- Fundo preto transparente (25% de opacidade)
- Texto branco centralizado com fonte Consolas
- Tamanho dinâmico - adapta ao IP (192.xxx.xxx.xxx)
- Auto-posicionamento - funciona em qualquer resolução
- Monitoramento automático de mudanças de IP/resolução
- Fechar: Duplo clique no texto
- Ultra leve: ~9 MB RAM, 0% CPU quando convertido para executavel

## Consumo de Recursos
Memória RAM: 9 MB
CPU: 0%
Tamanho EXE: ~13 MB (PyInstaller)

## Requisitos
- Python 3.6+
- Tkinter (padrão do Python)
- Windows 10/11

## Configurações Personalizáveis
```
TRANSPARENCIA   = 0.25          # 0.0 (invisível) a 1.0 (opaco)
HORIZONTAL      = 110           # Distância da borda direita
VERTICAL        = 60            # Distância da borda inferior
COR_FUNDO       = 'black'       # Denição da cor de fundo
COR_FONTE       = 'white'       # Definição da cor da fonte
PREFIXO_REDE    = '192.168.'     # Sua trava universal
```


## Estrutura do Projeto
```
ip_flutuante/
├── ip_flutuante.py      # Script principal
├── README.md            # Este arquivo
└── dist/
    └── ipNotificator.py # Executável (após PyInstaller)
```
## Instalação

### 1. Salvar Script
Recomendado salvar como ipNotificator.py

### 2. Executar Direto
python ipNotificator.py

### 3. PyInstaller (Executável)
pip install pyinstaller
pyinstaller --onefile --noconsole --windowed ipNotificator.py


## Funcionalidades Técnicas
1. Detecta IP interno (192.x.x.x preferencial)
2. Fallback: socket.gethostbyname()
3. Loop after(1000ms) - Zero CPU
4. winfo_screenwidth/height auto-ajuste
5. overrideredirect(True) - Sem bordas
6. place(relx=0.5, rely=0.5) - Centralizado


## Posicionamento
Canto inferior direito:
```
┌─ 155px da direita ──┐
│                     │
│                 60px│ ← Distância da taskbar
│   [ 192.168.0.13 ] │
└─────────────────────┘
```
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

Consumo de RAM:
→ Normal: 9 - 14 MB é OTIMIZADO!

## Licença
MIT License - Uso livre para fins pessoais/commerciais
© 2026 - Prefeitura Municipal de Monte Santo de Minas

---
Status: RODANDO PERFEITO | 9 MB RAM | 0% CPU
