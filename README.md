# Conversor de Holter/ECG

Este projeto converte arquivos de Holter e ECG do formato binário para o formato WFDB e gera visualizações dos dados.

## Estrutura do Projeto

```
.
├── src/
│   ├── holter_converter.py  # Conversor principal
│   ├── visualization.py     # Módulo de visualização
│   └── main.py             # Script principal
├── output/                 # Arquivos WFDB convertidos
├── plots/                  # Gráficos gerados
├── examples/              # Exemplos de uso
├── tests/                 # Testes unitários
└── requirements.txt       # Dependências
```

## Funcionalidades

- Conversão automática de arquivos binários para formato WFDB
- Detecção automática do tipo de exame (Holter ou ECG)
- Geração de visualizações:
  - Sinal temporal com espectro de frequência
  - Frequência cardíaca ao longo do tempo
  - Distribuição da frequência cardíaca
- Suporte a múltiplos canais
- Detecção de anotações e eventos

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/conversor-holter.git
cd conversor-holter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Conversão e Visualização

```bash
python src/main.py arquivo_entrada.bin [diretorio_saida] [diretorio_plots]
```

Exemplo:
```bash
python src/main.py examples/arquivo.bin output plots
```

### Visualização de Arquivos WFDB

```python
from src.visualization import SignalVisualizer

# Carrega e visualiza um arquivo WFDB
visualizer = SignalVisualizer("output/arquivo")
visualizer.load_data()

# Plota o sinal
visualizer.plot_signal(start_time=0, duration=10)

# Plota frequência cardíaca
visualizer.plot_heart_rate()

# Gera resumo completo
visualizer.plot_summary("plots")
```

## Visualizações Geradas

1. **Sinal Temporal**
   - Gráfico do sinal no domínio do tempo
   - Espectro de frequência
   - Escalas apropriadas para Holter/ECG

2. **Frequência Cardíaca**
   - Variação da FC ao longo do tempo
   - Suavização para melhor visualização
   - Detecção de picos R

3. **Distribuição da FC**
   - Histograma da frequência cardíaca
   - Análise estatística básica

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 