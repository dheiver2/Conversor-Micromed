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
Conversor-Micromed/
├── src/                    # Código fonte
│   ├── converters/         # Conversores para diferentes formatos
│   │   └── holter_converter.py  # Conversor principal
│   ├── analyzers/          # Analisadores de ECG
│   │   └── ecg_analyzer.py # Analisador de sinais
│   ├── utils/              # Utilitários
│   │   └── logger.py       # Configuração de logging
│   └── config.py           # Configurações do projeto
├── tests/                  # Testes unitários
├── examples/               # Exemplos de uso
│   └── intelligent_converter.py
├── archive/                # Arquivos de entrada
├── output/                 # Arquivos gerados
├── requirements.txt        # Dependências
└── README.md              # Documentação
```

## 📋 Requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`:
  - numpy>=1.21.0
  - scipy>=1.7.0
  - matplotlib>=3.4.0
  - wfdb>=3.4.0
  - pandas>=1.3.0
  - scikit-learn>=0.24.0
  - tqdm>=4.62.0
  - pytest>=6.2.0
  - pytest-cov>=2.12.0
  - black>=21.5b2
  - flake8>=3.9.0
  - mypy>=0.910
  - python-dotenv>=0.19.0

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/dheiver2/Conversor-Micromed.git
cd Conversor-Micromed
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Conversor Inteligente

O conversor inteligente analisa automaticamente o arquivo de entrada e gera apenas os arquivos necessários:

```python
from src.converters.holter_converter import HolterConverter

# Inicializa o conversor
converter = HolterConverter("arquivo.bin")

# Analisa o arquivo
converter.analyze_file_structure()

# Converte para WFDB
converter.convert_to_wfdb("output")
```

O conversor detecta automaticamente:
- Taxa de amostragem (com validação)
- Timestamp de início
- Presença de anotações
- Informações de arritmia
- Dados de qualidade

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
   - Número de amostras
   - Tamanho do arquivo

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