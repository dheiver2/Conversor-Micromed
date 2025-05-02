import os
from pathlib import Path
from typing import Dict, Any

# Diretórios do projeto
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Configurações de logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': 'converter.log',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Configurações do conversor
CONVERTER_CONFIG = {
    'default_sample_rate': 128,  # Hz
    'ecg_sample_rate': 500,      # Hz
    'holter_sample_rate': 128,   # Hz
    'min_duration_holter': 3600, # segundos
    'normalization': {
        'method': 'zscore',      # zscore ou minmax
        'clip': True,            # Limita valores extremos
        'clip_range': (-3, 3)    # Range para clipping
    },
    'peak_detection': {
        'height': 2.0,           # Múltiplos do desvio padrão
        'distance': 0.5,         # segundos
        'prominence': 1.0,       # Múltiplos do desvio padrão
        'width': 0.1            # segundos
    }
}

# Configurações de visualização
VISUALIZATION_CONFIG = {
    'plot': {
        'style': 'seaborn',      # Estilo do matplotlib
        'figsize': (15, 8),      # Tamanho da figura
        'dpi': 100,              # Resolução
        'linewidth': 0.5,        # Espessura da linha
        'alpha': 0.7             # Transparência
    },
    'signal': {
        'color': 'b',            # Cor do sinal
        'label': 'ECG',          # Rótulo
        'grid': True             # Grade
    },
    'peaks': {
        'color': 'r',            # Cor dos picos
        'marker': 'o',           # Marcador
        'size': 4                # Tamanho
    },
    'heart_rate': {
        'window': 60,            # Janela de suavização
        'color': 'b',            # Cor
        'grid': True             # Grade
    }
}

# Configurações de saída
OUTPUT_CONFIG = {
    'format': 'wfdb',           # Formato de saída
    'compression': False,       # Comprime arquivos
    'metadata': True,          # Salva metadados
    'annotations': True,       # Salva anotações
    'quality': True           # Salva informações de qualidade
}

# Configurações do analisador
ANALYZER_CONFIG: Dict[str, Any] = {
    "hrv_windows": [300,  # 5 minutos
                   600,   # 10 minutos
                   1800], # 30 minutos
    "arrhythmia_thresholds": {
        "tachycardia": 100,  # bpm
        "bradycardia": 60,   # bpm
        "pause": 2.0,        # segundos
    },
    "quality_metrics": {
        "snr_threshold": 10,  # dB
        "kurtosis_threshold": 5.0,
    }
}

# Configurações do visualizador
VISUALIZER_CONFIG: Dict[str, Any] = {
    "plot_style": "seaborn",
    "figure_size": (12, 6),
    "dpi": 300,
    "grid_alpha": 0.3,
    "line_width": 1.0,
}

# Cria diretórios necessários
for directory in [DATA_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True) 