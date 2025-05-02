import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import wfdb
import os
from scipy.signal import butter, filtfilt, find_peaks, correlate, welch, savgol_filter
from scipy.stats import norm, skew, kurtosis
from scipy.fft import fft, fftfreq
from scipy.ndimage import gaussian_filter1d
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import pywt
from biosppy.signals import ecg
from biosppy.tools import filter_signal
import heartpy as hp
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class SignalVisualizer:
    def __init__(self, record_path):
        """Inicializa o visualizador com o caminho do registro WFDB
        
        Args:
            record_path (str): Caminho para o arquivo WFDB (sem extensão)
        """
        self.record_path = record_path
        self.record_name = os.path.splitext(os.path.basename(record_path))[0]
        self.signal = None
        self.sample_rate = None
        self.exam_type = None
        self.annotations = None
        self.peaks = None
        self.rr_intervals = None
        self.heart_rates = None
        self.filtered_signal = None
        self.differentiated = None
        self.squared = None
        self.integrated = None
        self.wavelet_coeffs = None
        self.features = None
        self.quality_metrics = None
        self.arrhythmia_detection = None
        
    def _advanced_filtering(self, signal: np.ndarray) -> np.ndarray:
        """Aplica filtragem avançada usando múltiplas técnicas
        
        Args:
            signal (np.ndarray): Sinal de entrada
            
        Returns:
            np.ndarray: Sinal filtrado
        """
        # 1. Filtro Butterworth passa-banda
        nyquist = self.sample_rate / 2
        low = 5 / nyquist
        high = 15 / nyquist
        b, a = butter(4, [low, high], btype='band')
        filtered = filtfilt(b, a, signal)
        
        # 2. Filtro Savitzky-Golay para suavização
        filtered = savgol_filter(filtered, window_length=31, polyorder=3)
        
        # 3. Filtro Gaussiano adaptativo
        filtered = gaussian_filter1d(filtered, sigma=2)
        
        return filtered
    
    def _wavelet_transform(self, signal: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Aplica transformada wavelet para análise multirresolução
        
        Args:
            signal (np.ndarray): Sinal de entrada
            
        Returns:
            Tuple[np.ndarray, List[np.ndarray]]: Coeficientes wavelet
        """
        # Usa wavelet db4 (Daubechies 4) que é ótima para ECG
        wavelet = 'db4'
        level = 5
        coeffs = pywt.wavedec(signal, wavelet, level=level)
        
        # Reconstrução dos detalhes em cada nível
        reconstructed = []
        for i in range(1, len(coeffs)):
            coeffs_i = [np.zeros_like(c) for c in coeffs]
            coeffs_i[i] = coeffs[i]
            reconstructed.append(pywt.waverec(coeffs_i, wavelet))
        
        return coeffs, reconstructed
    
    def _extract_features(self, signal: np.ndarray, peaks: np.ndarray) -> Dict:
        """Extrai características avançadas do sinal
        
        Args:
            signal (np.ndarray): Sinal de entrada
            peaks (np.ndarray): Posições dos picos R
            
        Returns:
            Dict: Características extraídas
        """
        features = {}
        
        # 1. Características temporais
        rr_intervals = np.diff(peaks) / self.sample_rate
        features['mean_rr'] = np.mean(rr_intervals)
        features['std_rr'] = np.std(rr_intervals)
        features['rmssd'] = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        features['pnn50'] = np.sum(np.abs(np.diff(rr_intervals)) > 0.05) / len(rr_intervals) * 100
        
        # 2. Características espectrais
        f, Pxx = welch(signal, self.sample_rate, nperseg=1024)
        features['lf_power'] = np.sum(Pxx[(f >= 0.04) & (f <= 0.15)])
        features['hf_power'] = np.sum(Pxx[(f >= 0.15) & (f <= 0.4)])
        features['lf_hf_ratio'] = features['lf_power'] / features['hf_power']
        
        # 3. Características morfológicas
        features['skewness'] = skew(signal)
        features['kurtosis'] = kurtosis(signal)
        
        # 4. Características de complexidade
        features['sample_entropy'] = self._calculate_sample_entropy(signal)
        
        # 5. Características de variabilidade
        features['sdnn'] = np.std(rr_intervals)
        features['cv'] = features['sdnn'] / features['mean_rr']
        
        return features
    
    def _calculate_sample_entropy(self, signal: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """Calcula entropia amostral do sinal
        
        Args:
            signal (np.ndarray): Sinal de entrada
            m (int): Dimensão de embedding
            r (float): Tolerância
            
        Returns:
            float: Entropia amostral
        """
        N = len(signal)
        r = r * np.std(signal)
        
        def _phi(m):
            x = np.array([signal[i:i+m] for i in range(N-m+1)])
            C = np.sum([np.sum(np.abs(x[i] - x).max(axis=1) <= r) - 1 for i in range(N-m+1)])
            return C / ((N-m+1)*(N-m))
        
        return -np.log(_phi(m+1) / _phi(m))
    
    def _detect_peaks(self):
        """Detecta picos R usando o algoritmo de Pan-Tompkins com melhorias avançadas"""
        if self.signal is None:
            return
            
        # 1. Filtro passa-banda com múltiplos estágios
        nyquist = self.sample_rate / 2
        low = 5 / nyquist
        high = 15 / nyquist
        b, a = butter(4, [low, high], btype='band')
        self.filtered_signal = filtfilt(b, a, self.signal[:, 0])
        
        # 2. Diferenciação com suavização
        self.differentiated = np.diff(self.filtered_signal, prepend=self.filtered_signal[0])
        self.differentiated = savgol_filter(self.differentiated, window_length=15, polyorder=3)
        
        # 3. Elevação ao quadrado com normalização
        self.squared = self.differentiated ** 2
        self.squared = (self.squared - np.min(self.squared)) / (np.max(self.squared) - np.min(self.squared))
        
        # 4. Integração por janela móvel adaptativa
        window_size = int(0.15 * self.sample_rate)  # 150ms
        self.integrated = np.convolve(self.squared, np.ones(window_size)/window_size, mode='same')
        
        # 5. Detecção de picos com limiar adaptativo
        peak_threshold = np.mean(self.integrated) + 2 * np.std(self.integrated)
        noise_threshold = np.mean(self.integrated) + 0.5 * np.std(self.integrated)
        
        # Encontra candidatos a picos
        candidates, _ = find_peaks(self.integrated, 
                                 height=peak_threshold,
                                 distance=int(0.2 * self.sample_rate))  # Mínimo 0.2s entre picos
        
        # 6. Filtragem de picos usando correlação cruzada
        if len(candidates) > 0:
            # Cria template do primeiro pico
            template_size = int(0.1 * self.sample_rate)  # 100ms
            template = self.filtered_signal[max(0, candidates[0] - template_size//2):
                                          min(len(self.filtered_signal), candidates[0] + template_size//2)]
            
            # Refina posição dos picos
            refined_peaks = []
            for peak in candidates:
                # Extrai segmento ao redor do pico
                start = max(0, peak - template_size)
                end = min(len(self.filtered_signal), peak + template_size)
                segment = self.filtered_signal[start:end]
                
                if len(segment) >= len(template):
                    # Calcula correlação cruzada
                    correlation = correlate(segment, template, mode='valid')
                    offset = np.argmax(correlation) - len(template)//2
                    refined_peaks.append(peak + offset)
            
            self.peaks = np.array(refined_peaks)
            
            # 7. Filtragem de outliers usando estatísticas
            if len(self.peaks) > 1:
                rr_intervals = np.diff(self.peaks) / self.sample_rate
                mean_rr = np.mean(rr_intervals)
                std_rr = np.std(rr_intervals)
                
                # Remove picos com intervalos RR muito diferentes
                valid_peaks = [self.peaks[0]]
                for i in range(1, len(self.peaks)):
                    rr = (self.peaks[i] - self.peaks[i-1]) / self.sample_rate
                    if abs(rr - mean_rr) < 3 * std_rr:  # 3 desvios padrão
                        valid_peaks.append(self.peaks[i])
                
                self.peaks = np.array(valid_peaks)
        
        # 8. Calcula intervalos RR e frequência cardíaca
        if len(self.peaks) > 1:
            self.rr_intervals = np.diff(self.peaks) / self.sample_rate
            self.heart_rates = 60 / self.rr_intervals
            
            # 9. Extração de características
            self.features = self._extract_features(self.filtered_signal, self.peaks)
            
            # 10. Detecção de arritmias
            self._detect_arrhythmias()
    
    def _detect_arrhythmias(self) -> None:
        """Detecta diferentes tipos de arritmias usando múltiplos critérios"""
        if self.rr_intervals is None or len(self.rr_intervals) < 10:
            return
            
        self.arrhythmia_detection = {
            'tachycardia': False,
            'bradycardia': False,
            'premature_beat': False,
            'pause': False,
            'afib': False,
            'bigeminy': False,
            'trigeminy': False,
            'ventricular_tachycardia': False
        }
        
        # 1. Taquicardia e Bradicardia
        mean_hr = np.mean(self.heart_rates)
        if mean_hr > 100:
            self.arrhythmia_detection['tachycardia'] = True
        elif mean_hr < 60:
            self.arrhythmia_detection['bradycardia'] = True
        
        # 2. Batimentos prematuros e arritmias ventriculares
        rr_std = np.std(self.rr_intervals)
        if rr_std > 0.2:  # Alta variabilidade
            self.arrhythmia_detection['premature_beat'] = True
            
            # Verifica padrões de bigeminy e trigeminy
            rr_ratio = self.rr_intervals[1:] / self.rr_intervals[:-1]
            if np.mean(rr_ratio < 0.8) > 0.3:  # Muitos intervalos curtos
                if np.mean(rr_ratio[::2] < 0.8) > 0.5:  # Padrão alternado
                    self.arrhythmia_detection['bigeminy'] = True
                elif np.mean(rr_ratio[::3] < 0.8) > 0.5:  # Padrão a cada três
                    self.arrhythmia_detection['trigeminy'] = True
        
        # 3. Pausas
        if np.any(self.rr_intervals > 2.0):  # Pausa > 2 segundos
            self.arrhythmia_detection['pause'] = True
        
        # 4. Fibrilação Atrial
        if (self.features['sample_entropy'] > 1.5 and  # Alta irregularidade
            self.features['pnn50'] > 20 and  # Alta variabilidade
            self.features['lf_hf_ratio'] < 0.5):  # Dominância de HF
            self.arrhythmia_detection['afib'] = True
        
        # 5. Taquicardia Ventricular
        if (mean_hr > 120 and  # FC alta
            self.features['kurtosis'] > 5 and  # Distribuição leptocúrtica
            self.features['rmssd'] < 20):  # Baixa variabilidade
            self.arrhythmia_detection['ventricular_tachycardia'] = True
    
    def _calculate_quality_metrics(self) -> Dict:
        """Calcula métricas de qualidade do sinal
        
        Returns:
            Dict: Métricas de qualidade
        """
        if self.signal is None:
            return {}
            
        metrics = {}
        
        # 1. Relação Sinal-Ruído (SNR)
        signal_power = np.mean(self.signal[:, 0] ** 2)
        noise_power = np.mean((self.signal[:, 0] - self.filtered_signal) ** 2)
        metrics['snr'] = 10 * np.log10(signal_power / noise_power)
        
        # 2. Taxa de detecção de picos
        if self.annotations is not None and self.peaks is not None:
            true_positives = len(set(self.annotations.sample) & set(self.peaks))
            metrics['detection_rate'] = true_positives / len(self.annotations.sample)
        
        # 3. Regularidade do ritmo
        if self.rr_intervals is not None:
            metrics['rr_regularity'] = 1 - (np.std(self.rr_intervals) / np.mean(self.rr_intervals))
        
        # 4. Qualidade espectral
        f, Pxx = welch(self.signal[:, 0], self.sample_rate)
        metrics['spectral_quality'] = np.sum(Pxx[(f >= 0.5) & (f <= 40)]) / np.sum(Pxx)
        
        # 5. Qualidade morfológica
        metrics['morphological_quality'] = self.features['kurtosis'] if self.features else None
        
        return metrics
    
    def plot_advanced_analysis(self, start_time: float = 0, duration: float = 10, save_path: Optional[str] = None) -> None:
        """Plota análise avançada do sinal
        
        Args:
            start_time (float): Tempo inicial em segundos
            duration (float): Duração do segmento em segundos
            save_path (str, optional): Caminho para salvar o gráfico
        """
        if self.signal is None:
            print("Dados não carregados. Use load_data() primeiro.")
            return
            
        # Converte tempo para amostras
        start_sample = int(start_time * self.sample_rate)
        num_samples = int(duration * self.sample_rate)
        end_sample = min(start_sample + num_samples, len(self.signal))
        
        # Cria figura
        fig = plt.figure(figsize=(20, 15))
        gs = GridSpec(4, 2, height_ratios=[1, 1, 1, 1])
        
        # 1. Sinal original e filtrado
        ax1 = fig.add_subplot(gs[0, :])
        time = np.arange(start_sample, end_sample) / self.sample_rate
        ax1.plot(time, self.signal[start_sample:end_sample, 0], 'b-', alpha=0.5, label='Original')
        ax1.plot(time, self.filtered_signal[start_sample:end_sample], 'g-', label='Filtrado')
        
        # Marca picos R
        mask = (self.peaks >= start_sample) & (self.peaks < end_sample)
        peaks_in_range = self.peaks[mask]
        if len(peaks_in_range) > 0:
            peak_times = peaks_in_range / self.sample_rate
            ax1.plot(peak_times, self.filtered_signal[peaks_in_range], 'ro', markersize=4, label='Picos R')
        
        ax1.set_title('Sinal Original e Filtrado com Picos R')
        ax1.grid(True)
        ax1.legend()
        
        # 2. Espectro de frequência
        ax2 = fig.add_subplot(gs[1, 0])
        f, Pxx = welch(self.filtered_signal[start_sample:end_sample], self.sample_rate)
        ax2.semilogy(f, Pxx)
        ax2.set_title('Espectro de Frequência')
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Potência')
        ax2.grid(True)
        
        # 3. Distribuição dos intervalos RR
        ax3 = fig.add_subplot(gs[1, 1])
        if self.rr_intervals is not None:
            ax3.hist(self.rr_intervals, bins=50, density=True)
            ax3.set_title('Distribuição dos Intervalos RR')
            ax3.set_xlabel('Intervalo RR (s)')
            ax3.set_ylabel('Densidade')
            ax3.grid(True)
        
        # 4. Frequência cardíaca ao longo do tempo
        ax4 = fig.add_subplot(gs[2, :])
        if self.heart_rates is not None:
            time_hr = self.peaks[1:] / self.sample_rate
            ax4.plot(time_hr, self.heart_rates, 'b-')
            ax4.set_title('Frequência Cardíaca ao Longo do Tempo')
            ax4.set_xlabel('Tempo (s)')
            ax4.set_ylabel('Frequência Cardíaca (bpm)')
            ax4.grid(True)
        
        # 5. Detecção de arritmias
        ax5 = fig.add_subplot(gs[3, :])
        if self.arrhythmia_detection is not None:
            arrhythmias = [k for k, v in self.arrhythmia_detection.items() if v]
            if arrhythmias:
                ax5.text(0.5, 0.5, 'Arritmias Detectadas:\n' + '\n'.join(arrhythmias),
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax5.transAxes, fontsize=12)
            else:
                ax5.text(0.5, 0.5, 'Nenhuma arritmia detectada',
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax5.transAxes, fontsize=12)
        ax5.axis('off')
        
        # Ajusta layout
        plt.tight_layout()
        
        # Salva ou mostra o gráfico
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def get_analysis_report(self) -> Dict:
        """Gera relatório completo da análise
        
        Returns:
            Dict: Relatório com todas as métricas e detecções
        """
        report = {
            'basic_info': {
                'record_name': self.record_name,
                'exam_type': self.exam_type,
                'duration': len(self.signal) / self.sample_rate if self.signal is not None else None,
                'sample_rate': self.sample_rate
            },
            'signal_quality': self._calculate_quality_metrics(),
            'features': self.features,
            'arrhythmia_detection': self.arrhythmia_detection,
            'statistics': {
                'mean_hr': np.mean(self.heart_rates) if self.heart_rates is not None else None,
                'std_hr': np.std(self.heart_rates) if self.heart_rates is not None else None,
                'min_hr': np.min(self.heart_rates) if self.heart_rates is not None else None,
                'max_hr': np.max(self.heart_rates) if self.heart_rates is not None else None,
                'total_beats': len(self.peaks) if self.peaks is not None else None,
                'mean_rr': np.mean(self.rr_intervals) if self.rr_intervals is not None else None,
                'std_rr': np.std(self.rr_intervals) if self.rr_intervals is not None else None
            }
        }
        
        return report
    
    def load_data(self) -> bool:
        """Carrega os dados do arquivo WFDB
        
        Returns:
            bool: True se os dados foram carregados com sucesso
        """
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
            
            # Detecta picos R usando método avançado
            self._detect_peaks()
            
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False 