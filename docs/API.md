# API Documentation

## HolterConverter

Classe principal para conversão de arquivos de Holter/ECG.

### `__init__(input_dir: str, output_dir: str)`

Inicializa o conversor.

**Parâmetros:**
- `input_dir`: Diretório de entrada com arquivos .dat
- `output_dir`: Diretório de saída para arquivos WFDB

### `convert_file(dat_file: str) -> Optional[str]`

Converte um arquivo .dat para formato WFDB.

**Parâmetros:**
- `dat_file`: Caminho do arquivo .dat

**Retorna:**
- Caminho do arquivo convertido ou None em caso de erro

### `convert_directory() -> List[str]`

Converte todos os arquivos .dat no diretório de entrada.

**Retorna:**
- Lista de arquivos convertidos com sucesso

### `get_metadata() -> Dict`

Retorna metadados dos arquivos convertidos.

**Retorna:**
- Dicionário com metadados

## SignalVisualizer

Classe para visualização e análise de sinais.

### `__init__(record_path: str)`

Inicializa o visualizador.

**Parâmetros:**
- `record_path`: Caminho para o arquivo WFDB (sem extensão)

### `load_data() -> bool`

Carrega os dados do arquivo WFDB.

**Retorna:**
- True se os dados foram carregados com sucesso

### `plot_signal(start_time: float = 0, duration: float = 10, save_path: Optional[str] = None)`

Plota o sinal para um intervalo específico.

**Parâmetros:**
- `start_time`: Tempo inicial em segundos
- `duration`: Duração do segmento em segundos
- `save_path`: Caminho para salvar o gráfico

### `plot_heart_rate(window_size: int = 60, save_path: Optional[str] = None)`

Plota a frequência cardíaca ao longo do tempo.

**Parâmetros:**
- `window_size`: Tamanho da janela para suavização
- `save_path`: Caminho para salvar o gráfico

### `plot_summary(save_dir: Optional[str] = None)`

Gera um resumo visual do exame.

**Parâmetros:**
- `save_dir`: Diretório para salvar os gráficos

## Configurações

As configurações do projeto estão definidas em `src/config.py`:

### `LOGGING_CONFIG`

Configurações de logging:
- `version`: Versão do formato de logging
- `formatters`: Formatadores de log
- `handlers`: Handlers de log (console e arquivo)
- `loggers`: Configuração dos loggers

### `CONVERTER_CONFIG`

Parâmetros do conversor:
- `default_sample_rate`: Taxa de amostragem padrão (Hz)
- `ecg_sample_rate`: Taxa de amostragem para ECG (Hz)
- `holter_sample_rate`: Taxa de amostragem para Holter (Hz)
- `min_duration_holter`: Duração mínima para considerar Holter (s)
- `normalization`: Configurações de normalização
- `peak_detection`: Parâmetros de detecção de picos

### `VISUALIZATION_CONFIG`

Opções de visualização:
- `plot`: Configurações gerais de plotagem
- `signal`: Configurações do sinal
- `peaks`: Configurações dos picos
- `heart_rate`: Configurações da frequência cardíaca

### `OUTPUT_CONFIG`

Configurações de saída:
- `format`: Formato de saída
- `compression`: Comprime arquivos
- `metadata`: Salva metadados
- `annotations`: Salva anotações
- `quality`: Salva informações de qualidade 