import numpy as np
import wfdb
from typing import Dict, List, Optional
from scipy import signal
from scipy.stats import kurtosis

class ECGAnalyzer:
    """Analisador de sinais de ECG"""
    
    def __init__(self, record_path: str):
        """
        Inicializa o analisador com o caminho do registro WFDB
        
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
            
    def detect_qrs(self, signal: np.ndarray) -> np.ndarray:
        """
        Detecta complexos QRS no sinal de ECG
        
        Args:
            signal: Sinal de ECG
            
        Returns:
            Índices dos picos R
        """
        # Aplica filtro passa-banda
        nyquist = self.sample_rate / 2
        low = 5 / nyquist
        high = 15 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal)
        
        # Aplica transformada de Hilbert
        analytic_signal = signal.hilbert(filtered)
        amplitude_envelope = np.abs(analytic_signal)
        
        # Detecta picos
        peaks, _ = signal.find_peaks(
            amplitude_envelope,
            height=np.mean(amplitude_envelope) + 2 * np.std(amplitude_envelope),
            distance=self.sample_rate * 0.2  # Mínimo 200ms entre batimentos
        )
        
        return peaks
        
    def calculate_hrv(self, r_peaks: np.ndarray) -> Dict:
        """
        Calcula métricas de HRV (Heart Rate Variability)
        
        Args:
            r_peaks: Índices dos picos R
            
        Returns:
            Dicionário com métricas de HRV
        """
        if len(r_peaks) < 2:
            return {}
            
        # Calcula intervalos RR
        rr_intervals = np.diff(r_peaks) / self.sample_rate * 1000  # em ms
        
        # Métricas no domínio do tempo
        mean_rr = np.mean(rr_intervals)
        sdnn = np.std(rr_intervals)
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        
        # Métricas no domínio da frequência
        f, pxx = signal.welch(rr_intervals, fs=1.0/mean_rr)
        vlf = np.trapz(pxx[(f >= 0.003) & (f < 0.04)])
        lf = np.trapz(pxx[(f >= 0.04) & (f < 0.15)])
        hf = np.trapz(pxx[(f >= 0.15) & (f < 0.4)])
        
        return {
            'mean_rr': mean_rr,
            'sdnn': sdnn,
            'rmssd': rmssd,
            'vlf_power': vlf,
            'lf_power': lf,
            'hf_power': hf,
            'lf_hf_ratio': lf/hf if hf > 0 else 0
        }
        
    def detect_arrhythmias(self, r_peaks: np.ndarray) -> List[Dict]:
        """
        Detecta arritmias baseado nos intervalos RR
        
        Args:
            r_peaks: Índices dos picos R
            
        Returns:
            Lista de eventos de arritmia detectados
        """
        if len(r_peaks) < 3:
            return []
            
        arrhythmias = []
        rr_intervals = np.diff(r_peaks) / self.sample_rate * 1000  # em ms
        mean_rr = np.mean(rr_intervals)
        
        # Detecta pausas sinusais (> 2 segundos)
        pause_threshold = 2000  # ms
        pause_indices = np.where(rr_intervals > pause_threshold)[0]
        for idx in pause_indices:
            arrhythmias.append({
                'type': 'pause',
                'start': r_peaks[idx],
                'duration': rr_intervals[idx],
                'severity': 'severe' if rr_intervals[idx] > 3000 else 'moderate'
            })
            
        # Detecta taquicardia (> 100 bpm)
        tachycardia_threshold = 600  # ms (100 bpm)
        tachycardia_indices = np.where(rr_intervals < tachycardia_threshold)[0]
        for idx in tachycardia_indices:
            arrhythmias.append({
                'type': 'tachycardia',
                'start': r_peaks[idx],
                'duration': rr_intervals[idx],
                'severity': 'severe' if rr_intervals[idx] < 400 else 'moderate'
            })
            
        # Detecta bradicardia (< 60 bpm)
        bradycardia_threshold = 1000  # ms (60 bpm)
        bradycardia_indices = np.where(rr_intervals > bradycardia_threshold)[0]
        for idx in bradycardia_indices:
            arrhythmias.append({
                'type': 'bradycardia',
                'start': r_peaks[idx],
                'duration': rr_intervals[idx],
                'severity': 'severe' if rr_intervals[idx] > 2000 else 'moderate'
            })
            
        return arrhythmias
        
    def analyze(self) -> Dict:
        """
        Realiza análise completa do ECG
        
        Returns:
            Dicionário com resultados da análise
        """
        # Carrega o registro
        self.load_record()
        
        # Detecta complexos QRS
        r_peaks = self.detect_qrs(self.ecg_data)
        
        # Calcula métricas
        hrv_metrics = self.calculate_hrv(r_peaks)
        arrhythmias = self.detect_arrhythmias(r_peaks)
        
        # Análise de qualidade do sinal
        signal_quality = self.analyze_signal_quality()
        
        return {
            'hrv_metrics': hrv_metrics,
            'arrhythmias': arrhythmias,
            'signal_quality': signal_quality,
            'num_beats': len(r_peaks),
            'duration': len(self.ecg_data) / self.sample_rate,
            'sample_rate': self.sample_rate
        }
        
    def analyze_signal_quality(self) -> Dict:
        """
        Analisa a qualidade do sinal de ECG
        
        Returns:
            Dicionário com métricas de qualidade
        """
        # Calcula SNR (Signal-to-Noise Ratio)
        signal_power = np.mean(self.ecg_data ** 2)
        noise_power = np.mean((self.ecg_data - signal.medfilt(self.ecg_data, kernel_size=21)) ** 2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
        
        # Calcula kurtosis (medida de outliers)
        kurt = kurtosis(self.ecg_data)
        
        # Detecta saturação
        max_value = np.max(np.abs(self.ecg_data))
        saturation = max_value > 0.9  # Assumindo que o sinal é normalizado
        
        return {
            'snr': snr,
            'kurtosis': kurt,
            'saturation': saturation,
            'quality': 'good' if snr > 20 and not saturation else 'poor'
        } 