# ipNotificator - IP Flutuante & Monitor de Eventos

## Descrição
O **ipNotificator** é um overlay minimalista e ultra-leve projetado para exibir o endereço IP 
interno da rede em tempo real, agora com um sistema integrado de **datas comemorativas**. 
Posicionado discretamente no canto inferior direito, ele é a ferramenta ideal para administradores 
de rede, desenvolvedores e técnicos que precisam dessa informação de forma rápida sem interrupções.

## Características
- Sempre visível (mas não atrapalha)
- Fundo preto transparente (25% de opacidade)
- Texto branco centralizado com fonte Consolas
- Tamanho dinâmico - adapta ao IP (192.xxx.xxx.xxx)
- Auto-posicionamento - funciona em qualquer resolução
- Monitoramento automático de mudanças de IP/resolução
- Fechar: Triplo clique no texto
- Ultra leve: ~9 MB RAM, 0% CPU quando convertido para executavel
- **Sistema de Datas Comemorativas**: Exibe emojis e frases personalizadas em datas específicas (Natal, Ano Novo, Dia do Programador, etc.).
- **Menu de Contexto (Botão Direito)**:
    - **Copiar IP**: Copia instantaneamente o endereço para a área de transferência.
    - **Atualizar**: Força a atualização do IP e recarrega as datas.
    - **Editar Datas**: Interface gráfica integrada para adicionar ou modificar eventos.
- **Otimização Extrema**: Uso de cache global e Garbage Collector (GC) para manter o consumo de RAM entre 9MB e 14MB.
- **Easter Eggs**: Interações especiais escondidas (como o modo antigravidade e o contador 42).

## Consumo de Recursos
| Recurso | Desempenho |
| :--- | :--- |
| **Memória RAM** | ~9 MB (Otimizado com GC) |
| **CPU** | 0% (Monitoramento em background) |
| **Tamanho EXE** | ~13 MB (PyInstaller) |
| **Refresh Rate** | 15 segundos (Inteligente) |

## Requisitos
- **Python 3.6+**
- **Tkinter** (Biblioteca padrão do Python)
- **Windows 10/11** (Suporte a transparência e fontes do sistema)

## Configurações Personalizáveis
As configurações principais podem ser ajustadas diretamente no topo do script:



## Configurações Personalizáveis
```python

TRANSPARENCIA   = 0.25          # 0.0 (invisível) a 1.0 (opaco)
HORIZONTAL      = 110           # Distância da borda direita
VERTICAL        = 60            # Distância da borda inferior
COR_FUNDO       = 'black'       # Denição da cor de fundo
COR_FONTE       = 'white'       # Definição da cor da fonte
PREFIXO_REDE    = '192.168.'    # Sua trava universal
TAMANHO_FONTE   = 10            # Tamanho da fonte Consolas/Segoe UI
CONFIG_FILE     = 'ip_widget_datas.json' # Arquivo de armazenamento das datas
```

## Estrutura do Projeto
```text
ip_flutuante/
├── ipNotificator.py      # Script principal (v1.3)
├── ip_widget_datas.json  # Banco de dados de eventos (gerado automaticamente)
├── README.md             # Documentação do projeto
└── dist/
    └── ipNotificator.exe # Executável final
```

## Funcionalidades Técnicas
1.  **Detecção Inteligente**: Prioriza IPs na faixa definida em `PREFIXO_REDE` com fallback para `socket.getaddrinfo`.
2.  **Gerenciamento de Memória**: Implementação de `gc.collect()` em ciclos estratégicos para evitar vazamentos de memória.
3.  **Interface Adaptativa**: O tamanho do overlay se ajusta dinamicamente ao comprimento do IP ou da frase comemorativa.
4.  **Persistência**: Datas personalizadas são salvas em um arquivo JSON local, permitindo edições sem alterar o código-fonte.

## Como Usar
1.  **Execução**: Rode o script `python ipNotificator.py` ou o executável.
2.  **Interação**:
    - **Botão Direito**: Abre o menu de opções (Copiar, Atualizar, Editar).
    - **Triplo Clique**: Fecha o aplicativo com segurança.
    - **Clique Simples**: Interage com o contador interno (Easter Egg).
3.  **Edição de Datas**: No menu "Editar Datas", use o formato `DD-MM | 🚀 Frase` para personalizar seus alertas.

## Instalação e Compilação
Para transformar o script em um executável Windows:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --windowed --icon=app.ico ipNotificator.py
```

---
> **Dica**: Se o IP não aparecer, verifique se o seu `PREFIXO_REDE` corresponde ao início do seu IP local (ex: 10.0 ou 192.168).


> Consumo de RAM: Normal: 9 - 14 MB é OTIMIZADO!

## Licença
MIT License - Uso livre para fins pessoais/commerciais
© 2026 - Prefeitura Municipal de Monte Santo de Minas

---
Status: RODANDO PERFEITO | 9 MB RAM | 0% CPU
