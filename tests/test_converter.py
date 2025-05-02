import os
import numpy as np
import pytest
from src.holter_converter import HolterConverter
from src.visualization import SignalVisualizer

@pytest.fixture
def converter():
    """Cria uma instância do conversor para testes"""
    input_dir = "test_data/input"
    output_dir = "test_data/output"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    return HolterConverter(input_dir, output_dir)

@pytest.fixture
def sample_data():
    """Gera dados de exemplo para testes"""
    # Gera 1 minuto de dados a 128 Hz (Holter)
    fs = 128
    t = np.arange(0, 60, 1/fs)
    signal = np.sin(2*np.pi*1*t) + 0.5*np.sin(2*np.pi*2*t)
    return signal.astype(np.int16)

def test_validate_input(converter, tmp_path):
    """Testa validação de entrada"""
    # Arquivo não existe
    assert not converter._validate_input("nonexistent.dat")
    
    # Arquivo com extensão errada
    wrong_ext = tmp_path / "test.txt"
    wrong_ext.write_text("test")
    assert not converter._validate_input(str(wrong_ext))
    
    # Arquivo válido
    valid_file = tmp_path / "test.dat"
    valid_file.write_bytes(b"test")
    assert converter._validate_input(str(valid_file))

def test_detect_sample_rate(converter, sample_data):
    """Testa detecção de taxa de amostragem"""
    # Testa com dados de Holter (1 minuto a 128 Hz)
    rate = converter._detect_sample_rate(sample_data)
    assert rate == 128
    assert converter.exam_type == 'holter'
    
    # Testa com dados de ECG (10 segundos a 500 Hz)
    ecg_data = np.tile(sample_data, 10)
    rate = converter._detect_sample_rate(ecg_data)
    assert rate == 500
    assert converter.exam_type == 'ecg'

def test_process_signal(converter, sample_data):
    """Testa processamento do sinal"""
    processed_data, stats = converter._process_signal(sample_data)
    
    # Verifica normalização
    assert np.isclose(np.mean(processed_data), 0, atol=1e-10)
    assert np.isclose(np.std(processed_data), 1, atol=1e-10)
    
    # Verifica estatísticas
    assert 'mean' in stats
    assert 'std' in stats
    assert 'min' in stats
    assert 'max' in stats
    assert 'duration' in stats

def test_convert_file(converter, tmp_path, sample_data):
    """Testa conversão de arquivo"""
    # Cria arquivo de teste
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(sample_data.tobytes())
    
    # Converte arquivo
    output_file = converter.convert_file(str(test_file))
    assert output_file is not None
    
    # Verifica se arquivos foram criados
    assert os.path.exists(output_file + ".dat")
    assert os.path.exists(output_file + ".hea")
    
    # Verifica metadados
    metadata = converter.get_metadata()
    assert "test" in metadata
    assert metadata["test"]["exam_type"] == "holter"
    assert metadata["test"]["sample_rate"] == 128

def test_convert_directory(converter, tmp_path, sample_data):
    """Testa conversão de diretório"""
    # Cria arquivos de teste
    for i in range(3):
        test_file = tmp_path / f"test_{i}.dat"
        test_file.write_bytes(sample_data.tobytes())
    
    # Converte diretório
    converter.input_dir = str(tmp_path)
    converted_files = converter.convert_directory()
    
    # Verifica resultados
    assert len(converted_files) == 3
    assert all(os.path.exists(f + ".dat") for f in converted_files)
    assert all(os.path.exists(f + ".hea") for f in converted_files)
    
    # Verifica metadados
    metadata = converter.get_metadata()
    assert len(metadata) == 3

def test_visualization(converter, tmp_path, sample_data):
    """Testa visualização do sinal"""
    # Cria e converte arquivo de teste
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(sample_data.tobytes())
    output_file = converter.convert_file(str(test_file))
    
    # Cria visualizador
    visualizer = SignalVisualizer(output_file)
    assert visualizer.load_data()
    
    # Testa plotagem
    visualizer.plot_signal(0, 5)
    visualizer.plot_heart_rate()
    visualizer.plot_summary() 