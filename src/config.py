import os
from pathlib import Path
from typing import Dict, Any

# Diretórios do projeto
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Configurações do conversor
CONVERTER_CONFIG: Dict[str, Any] = {
    "sample_rate": 1000,  # Hz
    "voltage_scale": 0.001,  # mV
    "header_size": 1024,  # bytes
    "annotation_size": 1024,  # bytes
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