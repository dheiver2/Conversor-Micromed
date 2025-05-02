# Conversor de Holter/ECG

Este projeto é um conversor de arquivos de Holter e ECG para o formato WFDB (Waveform Database), com recursos de visualização e análise de sinais.

## Funcionalidades

- Conversão automática de arquivos .dat para formato WFDB
- Detecção inteligente do tipo de exame (Holter ou ECG)
- Detecção automática da taxa de amostragem
- Visualização interativa dos sinais
- Análise de frequência cardíaca
- Detecção de picos R
- Exportação de metadados e estatísticas

## Requisitos

- Python 3.8+
- NumPy
- SciPy
- WFDB
- Matplotlib
- Seaborn
- Pytest (para testes)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/conversor-holter.git
cd conversor-holter
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Conversão de Arquivos

```python
from src.holter_converter import HolterConverter

# Inicializa o conversor
converter = HolterConverter("diretorio_entrada", "diretorio_saida")

# Converte um arquivo específico
arquivo_convertido = converter.convert_file("arquivo.dat")

# Converte todos os arquivos de um diretório
arquivos_convertidos = converter.convert_directory()
```

### Visualização

```python
from src.visualization import SignalVisualizer

# Inicializa o visualizador
visualizer = SignalVisualizer("arquivo_wfdb")

# Carrega os dados
visualizer.load_data()

# Visualiza o sinal
visualizer.plot_signal(0, 10)  # Primeiros 10 segundos

# Visualiza frequência cardíaca
visualizer.plot_heart_rate()

# Gera resumo completo
visualizer.plot_summary()
```

## Estrutura do Projeto

```
conversor-holter/
├── src/
│   ├── __init__.py
│   ├── holter_converter.py    # Conversor principal
│   ├── visualization.py       # Visualização e análise
│   └── config.py             # Configurações
├── tests/
│   ├── __init__.py
│   └── test_converter.py     # Testes unitários
├── requirements.txt          # Dependências
└── README.md                # Documentação
```

## Configuração

As configurações do projeto podem ser ajustadas no arquivo `src/config.py`:

- `LOGGING_CONFIG`: Configurações de logging
- `CONVERTER_CONFIG`: Parâmetros do conversor
- `VISUALIZATION_CONFIG`: Opções de visualização
- `OUTPUT_CONFIG`: Configurações de saída

## Testes

Para executar os testes:

```bash
pytest tests/
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Seu Nome - seu.email@exemplo.com

Link do Projeto: [https://github.com/seu-usuario/conversor-holter](https://github.com/seu-usuario/conversor-holter) 