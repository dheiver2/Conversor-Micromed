import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import wfdb
from typing import Optional, Tuple
import os

class ECGPlotter:
    """Visualizador de sinais de ECG"""
    
    def __init__(self, record_path: str):
        """
        Inicializa o visualizador com o caminho do registro WFDB
        
        Args:
            record_path: Caminho para o registro WFDB
        """
        self.record_path = record_path
        self.record = None
        self.annotations = None
        self.ecg_data = None
        self.sample_rate = None
        
    def load_record(self) -> None:
        """Carrega o registro WFDB e suas anotações"""
        try:
            self.record = wfdb.rdrecord(self.record_path)
            self.ecg_data = self.record.p_signal[:, 0]
            self.sample_rate = self.record.fs
            
            # Tenta carregar anotações
            try:
                self.annotations = wfdb.rdann(self.record_path, 'atr')
            except:
                self.annotations = None
                
        except Exception as e:
            raise ValueError(f"Erro ao carregar registro: {e}")
            
    def plot_segment(self, 
                    start_time: float = 0,
                    duration: float = 10,
                    output_dir: str = 'output',
                    show_grid: bool = True,
                    show_annotations: bool = True) -> None:
        """
        Plota um segmento do ECG
        
        Args:
            start_time: Tempo inicial em segundos
            duration: Duração do segmento em segundos
            output_dir: Diretório de saída para o gráfico
            show_grid: Se deve mostrar a grade
            show_annotations: Se deve mostrar as anotações
        """
        # Carrega o registro se necessário
        if self.record is None:
            self.load_record()
            
        # Calcula índices do segmento
        start_idx = int(start_time * self.sample_rate)
        end_idx = int((start_time + duration) * self.sample_rate)
        
        # Extrai o segmento
        segment = self.ecg_data[start_idx:end_idx]
        time = np.arange(len(segment)) / self.sample_rate
        
        # Cria a figura
        fig = plt.figure(figsize=(20, 10))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        # Plota o ECG
        ax.plot(time, segment, 'k-', linewidth=0.5)
        
        # Configura a grade
        if show_grid:
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xticks(np.arange(0, duration, 0.2))  # Linhas verticais a cada 0.2s
            ax.set_yticks(np.arange(-2, 2, 0.5))  # Linhas horizontais a cada 0.5mV
            
        # Configura os eixos
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Amplitude (mV)')
        ax.set_title(f'ECG - {os.path.basename(self.record_path)}')
        
        # Adiciona escala
        # Linha horizontal de 1mV
        ax.plot([duration-1, duration], [1, 1], 'k-', linewidth=2)
        # Linha vertical de 0.2s
        ax.plot([duration-0.2, duration], [1.5, 1.5], 'k-', linewidth=2)
        ax.text(duration-0.5, 1, '1 mV', ha='right')
        ax.text(duration-0.1, 1.5, '0.2 s', ha='right')
        
        # Ajusta limites
        ax.set_xlim(0, duration)
        ax.set_ylim(-2, 2)
        
        # Plota anotações se disponíveis
        if show_annotations and self.annotations is not None:
            for i, (sample, symbol) in enumerate(zip(self.annotations.sample, self.annotations.symbol)):
                if start_idx <= sample < end_idx:
                    time_ann = (sample - start_idx) / self.sample_rate
                    ax.plot([time_ann], [segment[sample - start_idx]], 'ro', markersize=4)
                    ax.text(time_ann, segment[sample - start_idx] + 0.2, symbol,
                           ha='center', color='red')
        
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva o gráfico
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{os.path.basename(self.record_path)}_ecg.png"), dpi=300)
        plt.close()
        
    def plot_hrv(self,
                output_dir: str = 'output',
                window_size: int = 300) -> None:
        """
        Plota análise de HRV
        
        Args:
            output_dir: Diretório de saída para o gráfico
            window_size: Tamanho da janela para análise em segundos
        """
        # Carrega o registro se necessário
        if self.record is None:
            self.load_record()
            
        # Detecta complexos QRS
        from src.analyzers.ecg_analyzer import ECGAnalyzer
        analyzer = ECGAnalyzer(self.record_path)
        r_peaks = analyzer.detect_qrs(self.ecg_data)
        
        # Calcula intervalos RR
        rr_intervals = np.diff(r_peaks) / self.sample_rate * 1000  # em ms
        
        # Cria a figura
        fig = plt.figure(figsize=(20, 10))
        gs = GridSpec(2, 1, figure=fig)
        
        # Plota tachograma
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(rr_intervals, 'b-')
        ax1.set_xlabel('Número do batimento')
        ax1.set_ylabel('Intervalo RR (ms)')
        ax1.set_title('Tachograma')
        ax1.grid(True)
        
        # Plota histograma
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.hist(rr_intervals, bins=50, density=True)
        ax2.set_xlabel('Intervalo RR (ms)')
        ax2.set_ylabel('Densidade')
        ax2.set_title('Histograma dos Intervalos RR')
        ax2.grid(True)
        
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva o gráfico
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{os.path.basename(self.record_path)}_hrv.png"), dpi=300)
        plt.close()
        
    def plot_arrhythmias(self,
                        output_dir: str = 'output',
                        window_size: int = 300) -> None:
        """
        Plota detecção de arritmias
        
        Args:
            output_dir: Diretório de saída para o gráfico
            window_size: Tamanho da janela para análise em segundos
        """
        # Carrega o registro se necessário
        if self.record is None:
            self.load_record()
            
        # Detecta arritmias
        from src.analyzers.ecg_analyzer import ECGAnalyzer
        analyzer = ECGAnalyzer(self.record_path)
        arrhythmias = analyzer.detect_arrhythmias(analyzer.detect_qrs(self.ecg_data))
        
        # Cria a figura
        fig = plt.figure(figsize=(20, 10))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        # Plota o ECG
        time = np.arange(len(self.ecg_data)) / self.sample_rate
        ax.plot(time, self.ecg_data, 'k-', linewidth=0.5)
        
        # Marca as arritmias
        colors = {
            'pause': 'red',
            'tachycardia': 'blue',
            'bradycardia': 'green'
        }
        
        for arr in arrhythmias:
            start_time = arr['start'] / self.sample_rate
            duration = arr['duration'] / 1000  # converter ms para s
            arr_type = arr['type']
            
            # Desenha retângulo para marcar a arritmia
            rect = plt.Rectangle(
                (start_time, -2),
                duration,
                4,
                facecolor=colors[arr_type],
                alpha=0.2
            )
            ax.add_patch(rect)
            
            # Adiciona texto
            ax.text(
                start_time + duration/2,
                1.8,
                f"{arr_type} ({arr['severity']})",
                ha='center',
                color=colors[arr_type]
            )
            
        # Configura o gráfico
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Amplitude (mV)')
        ax.set_title('Detecção de Arritmias')
        ax.grid(True)
        ax.set_xlim(0, len(self.ecg_data) / self.sample_rate)
        ax.set_ylim(-2, 2)
        
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva o gráfico
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{os.path.basename(self.record_path)}_arrhythmias.png"), dpi=300)
        plt.close() 