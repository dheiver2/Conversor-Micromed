import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_ecg_signal(duration=60, fs=128):
    """Gera um sinal ECG simulado
    
    Args:
        duration (float): Duração em segundos
        fs (int): Taxa de amostragem em Hz
        
    Returns:
        tuple: (tempo, sinal)
    """
    # Gera vetor de tempo
    t = np.arange(0, duration, 1/fs)
    
    # Frequências dos componentes
    f1 = 1.0  # Hz (batimentos cardíacos)
    f2 = 2.0  # Hz (segundo harmônico)
    f3 = 0.1  # Hz (respiração)
    
    # Gera componentes do sinal
    cardiac = np.sin(2*np.pi*f1*t)
    harmonic = 0.5*np.sin(2*np.pi*f2*t)
    respiration = 0.2*np.sin(2*np.pi*f3*t)
    
    # Combina componentes
    signal = cardiac + harmonic + respiration
    
    # Adiciona ruído
    noise = 0.1 * np.random.randn(len(t))
    signal += noise
    
    return t, signal

def generate_holter_signal(duration=3600, fs=128):
    """Gera um sinal Holter simulado com variações na FC
    
    Args:
        duration (float): Duração em segundos
        fs (int): Taxa de amostragem em Hz
        
    Returns:
        tuple: (tempo, sinal)
    """
    # Gera sinal base
    t, signal = generate_ecg_signal(duration, fs)
    
    # Adiciona variações na FC
    fc_variation = 0.2 * np.sin(2*np.pi*0.001*t)  # Variação lenta
    signal = signal * (1 + fc_variation)
    
    # Adiciona artefatos ocasionais
    artifacts = np.zeros_like(signal)
    for i in range(0, len(t), fs*60):  # A cada minuto
        if np.random.rand() < 0.1:  # 10% de chance
            start = i + np.random.randint(0, fs*5)
            end = start + np.random.randint(fs, fs*3)
            artifacts[start:end] = np.random.randn(end-start)
    
    signal += artifacts
    
    return t, signal

def save_signal(t, signal, filename, fs=128):
    """Salva sinal em arquivo .dat
    
    Args:
        t (np.ndarray): Vetor de tempo
        signal (np.ndarray): Sinal
        filename (str): Nome do arquivo
        fs (int): Taxa de amostragem
    """
    # Normaliza para int16
    signal = (signal * 32767).astype(np.int16)
    
    # Salva dados
    signal.tofile(filename)
    
    # Plota sinal
    plt.figure(figsize=(15, 5))
    plt.plot(t, signal)
    plt.title(f'Sinal {os.path.basename(filename)}')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.savefig(filename.replace('.dat', '.png'))
    plt.close()

def main():
    # Cria diretório de exemplos
    data_dir = Path("examples/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Gera exemplos
    print("Gerando exemplos...")
    
    # Exemplo de ECG (1 minuto)
    t, signal = generate_ecg_signal(60, 500)
    save_signal(t, signal, data_dir / "ecg_example.dat", 500)
    
    # Exemplo de Holter (1 hora)
    t, signal = generate_holter_signal(3600, 128)
    save_signal(t, signal, data_dir / "holter_example.dat", 128)
    
    print("Exemplos gerados em:", data_dir)

if __name__ == "__main__":
    main() 