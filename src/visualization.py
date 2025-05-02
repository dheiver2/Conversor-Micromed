import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import wfdb
import os

class SignalVisualizer:
    def __init__(self, record_path):
        """Inicializa o visualizador com o caminho do registro WFDB"""
        self.record_path = record_path
        self.record_name = os.path.splitext(os.path.basename(record_path))[0]
        self.signal = None
        self.sample_rate = None
        self.exam_type = None
        self.annotations = None
        
    def load_data(self):
        """Carrega os dados do arquivo WFDB"""
        try:
            # Carrega o sinal
            record = wfdb.rdrecord(self.record_path)
            self.signal = record.p_signal
            self.sample_rate = record.fs
            
            # Tenta carregar anotações se existirem
            try:
                self.annotations = wfdb.rdann(self.record_path, 'atr')
            except:
                self.annotations = None
            
            # Detecta o tipo de exame baseado na duração
            duration = len(self.signal) / self.sample_rate
            self.exam_type = 'holter' if duration > 3600 else 'ecg'
            
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def plot_signal(self, start_time=0, duration=10, save_path=None):
        """Plota o sinal para um intervalo específico"""
        if not self.signal is not None:
            print("Dados não carregados. Use load_data() primeiro.")
            return
        
        # Converte tempo para amostras
        start_sample = int(start_time * self.sample_rate)
        num_samples = int(duration * self.sample_rate)
        end_sample = min(start_sample + num_samples, len(self.signal))
        
        # Cria a figura
        fig = plt.figure(figsize=(15, 8))
        gs = GridSpec(2, 1, height_ratios=[3, 1])
        
        # Plota o sinal
        ax1 = fig.add_subplot(gs[0])
        time = np.arange(start_sample, end_sample) / self.sample_rate
        ax1.plot(time, self.signal[start_sample:end_sample, 0], 'b-', linewidth=0.5)
        ax1.set_title(f'Sinal {self.exam_type.upper()} - {self.record_name}')
        ax1.set_ylabel('Amplitude (mV)')
        ax1.grid(True)
        
        # Plota espectro de frequência
        ax2 = fig.add_subplot(gs[1])
        signal_segment = self.signal[start_sample:end_sample, 0]
        fft = np.fft.fft(signal_segment)
        freqs = np.fft.fftfreq(len(signal_segment), 1/self.sample_rate)
        ax2.plot(freqs[:len(freqs)//2], np.abs(fft)[:len(freqs)//2], 'r-')
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.grid(True)
        
        # Ajusta o layout
        plt.tight_layout()
        
        # Salva ou mostra o gráfico
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_heart_rate(self, window_size=60, save_path=None):
        """Plota a frequência cardíaca ao longo do tempo"""
        if not self.signal is not None:
            print("Dados não carregados. Use load_data() primeiro.")
            return
        
        # Detecta picos R (simplificado)
        signal = self.signal[:, 0]
        peaks = np.where(signal > np.mean(signal) + 2*np.std(signal))[0]
        
        # Calcula intervalos RR
        rr_intervals = np.diff(peaks) / self.sample_rate
        heart_rates = 60 / rr_intervals
        
        # Suaviza a frequência cardíaca
        window = np.ones(window_size) / window_size
        smoothed_hr = np.convolve(heart_rates, window, mode='valid')
        
        # Plota
        plt.figure(figsize=(15, 5))
        time = peaks[1:] / self.sample_rate / 60  # em minutos
        plt.plot(time[:len(smoothed_hr)], smoothed_hr, 'b-', linewidth=1)
        plt.title(f'Frequência Cardíaca - {self.record_name}')
        plt.xlabel('Tempo (minutos)')
        plt.ylabel('Frequência Cardíaca (bpm)')
        plt.grid(True)
        
        # Salva ou mostra o gráfico
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_summary(self, save_dir=None):
        """Gera um resumo visual do exame"""
        if not self.signal is not None:
            print("Dados não carregados. Use load_data() primeiro.")
            return
        
        # Cria diretório se necessário
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # Plota diferentes visualizações
        self.plot_signal(0, 10, 
                        save_path=os.path.join(save_dir, f"{self.record_name}_signal.png") if save_dir else None)
        self.plot_heart_rate(save_path=os.path.join(save_dir, f"{self.record_name}_hr.png") if save_dir else None)
        
        # Plota histograma da frequência cardíaca
        plt.figure(figsize=(10, 6))
        signal = self.signal[:, 0]
        peaks = np.where(signal > np.mean(signal) + 2*np.std(signal))[0]
        rr_intervals = np.diff(peaks) / self.sample_rate
        heart_rates = 60 / rr_intervals
        
        plt.hist(heart_rates, bins=50, density=True, alpha=0.7)
        plt.title(f'Distribuição da Frequência Cardíaca - {self.record_name}')
        plt.xlabel('Frequência Cardíaca (bpm)')
        plt.ylabel('Densidade')
        plt.grid(True)
        
        if save_dir:
            plt.savefig(os.path.join(save_dir, f"{self.record_name}_hist.png"), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show() 