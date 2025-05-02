# Conversor e Analisador de Holter

Um conjunto avançado de ferramentas para análise e conversão de arquivos de Holter para o formato WFDB.

## 🚀 Visão Geral

Este projeto fornece uma solução completa para:
- Conversão inteligente de arquivos BIN de Holter para formato WFDB
- Análise detalhada de sinais de ECG
- Detecção de arritmias
- Visualização de dados
- Geração de relatórios

## 📁 Estrutura do Projeto

```
holter-analyzer/
├── src/                    # Código fonte
│   ├── converters/         # Conversores para diferentes formatos
│   │   └── holter_converter.py  # Conversor principal
│   ├── analyzers/          # Analisadores de ECG
│   │   └── ecg_analyzer.py # Analisador de sinais
│   ├── utils/              # Utilitários
│   └── visualization/      # Visualização de dados
│       └── ecg_plotter.py  # Visualizador de ECG
├── tests/                  # Testes unitários
├── examples/               # Exemplos de uso
│   ├── convert_and_analyze.py
│   └── intelligent_converter.py
├── docs/                   # Documentação
└── data/                   # Dados de exemplo
```

## 📋 Requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/holter-analyzer.git
cd holter-analyzer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Conversão de Arquivos

```python
from src.converters.holter_converter import HolterConverter

# Inicializa o conversor
converter = HolterConverter("arquivo.bin")

# Analisa o arquivo
converter.analyze_file_structure()

# Converte para WFDB
converter.convert_to_wfdb("output")
```

### Análise de ECG

```python
from src.analyzers.ecg_analyzer import ECGAnalyzer

# Inicializa o analisador
analyzer = ECGAnalyzer("arquivo.wfdb")

# Realiza análise completa
results = analyzer.analyze()

# Acessa resultados
print(f"HRV: {results['hrv_metrics']}")
print(f"Arritmias: {results['arrhythmias']}")
```

### Visualização

```python
from src.visualization.ecg_plotter import ECGPlotter

# Inicializa o visualizador
plotter = ECGPlotter("arquivo.wfdb")

# Gera visualizações
plotter.plot_segment(duration=10)  # Plota 10 segundos
plotter.plot_hrv()                 # Plota análise de HRV
plotter.plot_arrhythmias()         # Plota detecção de arritmias
```

## 📊 Arquivos Gerados

O conversor gera automaticamente os seguintes arquivos, dependendo do conteúdo do arquivo de entrada:

1. **Arquivos Básicos** (sempre gerados):
   - `.hea`: Cabeçalho WFDB com metadados
   - `.dat`: Dados do ECG

2. **Arquivos de Anotação** (gerados se presentes):
   - `.atr`: Anotações de batimentos
   - `.ari`: Informações de arritmia
   - `.qrs`: Dados de qualidade do sinal

## 🔍 Detecção de Características

O conversor analisa automaticamente:

1. **Anotações**:
   - Detecta padrões nos últimos 1024 bytes
   - Identifica tipos de batimentos
   - Extrai timestamps

2. **Arritmias**:
   - Procura por códigos específicos
   - Classifica eventos
   - Calcula durações

3. **Qualidade do Sinal**:
   - Analisa SNR (Relação Sinal-Ruído)
   - Detecta saturação
   - Identifica artefatos

## 📈 Análise de HRV

O analisador calcula:

1. **Métricas no Domínio do Tempo**:
   - SDNN
   - RMSSD
   - pNN50

2. **Métricas no Domínio da Frequência**:
   - Potência VLF
   - Potência LF
   - Potência HF
   - Razão LF/HF

## 🎯 Detecção de Arritmias

O sistema detecta automaticamente:

1. **Taquicardia**:
   - Frequência > 100 bpm
   - Classificação de severidade

2. **Bradicardia**:
   - Frequência < 60 bpm
   - Classificação de severidade

3. **Pausas Sinusais**:
   - Duração > 2 segundos
   - Classificação de severidade

## 📝 Relatórios

O sistema gera relatórios detalhados incluindo:

1. **Metadados do Arquivo**:
   - Taxa de amostragem
   - Duração
   - Data/hora de início

2. **Resultados da Análise**:
   - Métricas de HRV
   - Eventos de arritmia
   - Qualidade do sinal

3. **Visualizações**:
   - Gráficos de ECG
   - Tachogramas
   - Histogramas de RR

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do email: seu-email@exemplo.com 