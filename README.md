# Conversor Inteligente de Holter para WFDB

Um conversor inteligente que analisa arquivos BIN de Holter e gera automaticamente os arquivos WFDB necessários, adaptando-se às características específicas de cada arquivo.

## 🚀 Características Principais

- **Conversão Inteligente**: Analisa automaticamente o arquivo de entrada e gera apenas os arquivos WFDB necessários
- **Detecção Automática**:
  - Anotações ECG
  - Arritmias
  - Qualidade do sinal
  - Taxa de amostragem
  - Timestamps
- **Arquivos WFDB Gerados**:
  - `.hea`: Cabeçalho com metadados
  - `.dat`: Dados do sinal ECG
  - `.atr`: Anotações (quando presentes)
  - `.ari`: Informações de arritmia (quando presentes)
  - `.qrs`: Informações de qualidade (quando presentes)

## 📁 Estrutura do Projeto

```
Conversor-Micromed/
├── src/
│   ├── converters/
│   │   └── holter_converter.py  # Conversor principal
│   ├── utils/
│   │   └── logger.py           # Utilitários de logging
│   └── config.py               # Configurações do projeto
├── tests/
│   └── test_converter.py       # Testes unitários
├── examples/
│   ├── intelligent_converter.py # Exemplo de uso
│   └── test_intelligent_conversion.py # Teste de conversão
├── archive/                    # Arquivos BIN de entrada
├── output/                     # Arquivos WFDB gerados
└── requirements.txt            # Dependências
```

## 📋 Requisitos

- Python 3.8+
- Bibliotecas:
  - numpy>=1.21.0
  - scipy>=1.7.0
  - wfdb>=4.0.0
  - matplotlib>=3.4.0
  - pandas>=1.3.0
  - scikit-learn>=0.24.0

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Conversor-Micromed.git
cd Conversor-Micromed
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Conversão Básica
```python
from src.converters.holter_converter import HolterConverter

# Inicializa o conversor
converter = HolterConverter("arquivo.bin")

# Analisa e converte
converter.analyze_file_structure()
converter.convert_to_wfdb("output")
```

### Conversão Inteligente
```python
from src.converters.holter_converter import HolterConverter

# Inicializa o conversor
converter = HolterConverter("arquivo.bin")

# Analisa o arquivo
converter.analyze_file_structure()

# Mostra quais arquivos serão gerados
print("Arquivos que serão gerados:")
for file_type in converter.required_files:
    print(f"- {file_type.name}")

# Converte para WFDB
converter.convert_to_wfdb("output")
```

## 📊 Arquivos Gerados

O conversor gera automaticamente os seguintes arquivos WFDB, dependendo das características do arquivo de entrada:

1. **Arquivos Obrigatórios**:
   - `.hea`: Cabeçalho com metadados do sinal
   - `.dat`: Dados do sinal ECG

2. **Arquivos Opcionais** (gerados quando presentes):
   - `.atr`: Anotações do ECG
   - `.ari`: Informações de arritmia
   - `.qrs`: Informações de qualidade do sinal

## 🔍 Detecção Inteligente

O conversor analisa automaticamente:

1. **Anotações**:
   - Detecta padrões nos últimos 1024 bytes
   - Extrai posição e tipo de cada anotação
   - Gera arquivo `.atr` quando encontradas

2. **Arritmias**:
   - Procura por códigos específicos no cabeçalho
   - Identifica tipo e severidade
   - Gera arquivo `.ari` quando encontradas

3. **Qualidade**:
   - Verifica flags de qualidade no cabeçalho
   - Avalia integridade dos dados
   - Gera arquivo `.qrs` com informações de qualidade

## 📈 Análise de Dados

O conversor extrai e processa:

1. **Metadados**:
   - Taxa de amostragem
   - Timestamp inicial
   - Duração do registro
   - Número de amostras
   - Tamanho do arquivo

2. **Estatísticas**:
   - Número de anotações
   - Número de arritmias
   - Qualidade do sinal
   - Presença de artefatos

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do email: seu-email@exemplo.com 