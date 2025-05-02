import pytest
import numpy as np
from pathlib import Path
from src.converters.holter_converter import HolterConverter
from src.config import CONVERTER_CONFIG

def test_converter_initialization():
    """Testa a inicialização do conversor"""
    converter = HolterConverter("test.bin")
    assert converter.bin_file == "test.bin"
    assert converter.sample_rate == CONVERTER_CONFIG["sample_rate"]

def test_header_analysis():
    """Testa a análise do cabeçalho"""
    converter = HolterConverter("test.bin")
    # Simula dados do cabeçalho
    header_bytes = bytes([0] * CONVERTER_CONFIG["header_size"])
    converter._extract_metadata(header_bytes)
    assert converter.sample_rate == CONVERTER_CONFIG["sample_rate"]

def test_annotation_detection():
    """Testa a detecção de anotações"""
    converter = HolterConverter("test.bin")
    # Simula dados de anotação
    annotation_bytes = bytes([1] * CONVERTER_CONFIG["annotation_size"])
    assert not converter._has_annotations(annotation_bytes)

def test_arrhythmia_detection():
    """Testa a detecção de arritmias"""
    converter = HolterConverter("test.bin")
    # Simula dados do cabeçalho
    header_bytes = bytes([0] * CONVERTER_CONFIG["header_size"])
    assert not converter._has_arrhythmia_info(header_bytes)

def test_quality_detection():
    """Testa a detecção de qualidade"""
    converter = HolterConverter("test.bin")
    # Simula dados do cabeçalho
    header_bytes = bytes([0] * CONVERTER_CONFIG["header_size"])
    assert not converter._has_quality_info(header_bytes)

def test_file_generation(tmp_path):
    """Testa a geração de arquivos"""
    converter = HolterConverter("test.bin")
    output_dir = tmp_path / "output"
    converter.convert_to_wfdb(str(output_dir))
    assert output_dir.exists() 