import struct
import numpy as np
import pandas as pd
from datetime import datetime
import wfdb
import os
import re

class HolterConverter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_data = None
        self.sample_rate = None
        self.start_time = None
        self.signal_data = None
        self.record_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Constantes do formato do arquivo
        self.HEADER_SIZE = 1024
        self.BYTES_PER_SAMPLE = 2
        
        # Parâmetros específicos para cada tipo de exame
        self.exam_type = None
        self.exam_params = {
            'holter': {
                'default_sample_rate': 128,
                'common_rates': [128, 256, 512],
                'min_duration': 3600,  # 1 hora
                'min_std': 50
            },
            'ecg': {
                'default_sample_rate': 500,
                'common_rates': [250, 500, 1000],
                'min_duration': 10,  # 10 segundos
                'min_std': 100
            }
        }
        
        # Flags para determinar quais arquivos gerar
        self.has_signal_data = False
        self.has_annotations = False
        self.has_arrhythmia = False
        
        # Dicionário de códigos de arritmia
        self.arrhythmia_codes = {
            1: 'N',  # Normal
            2: 'V',  # Ventricular
            3: 'S',  # Supraventricular
            4: 'F',  # Fibrilação
            5: 'Q'   # Pausa/QRS não detectado
        }
        
        # Lista para armazenar anotações
        self.annotations = []

    def detect_exam_type(self, data_length, sample_rate):
        """Detecta automaticamente se é Holter ou ECG baseado nas características dos dados"""
        duration_seconds = data_length / sample_rate
        
        if duration_seconds > 3600:  # Mais de 1 hora
            return 'holter'
        else:
            return 'ecg'

    def read_bin_file(self):
        """Lê o arquivo BIN e extrai os dados brutos"""
        try:
            with open(self.file_path, 'rb') as file:
                self.raw_data = file.read()
            return True
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return False

    def analyze_header(self):
        """Analisa o cabeçalho do arquivo para extrair informações importantes"""
        if not self.raw_data:
            return False

        try:
            header = self.raw_data[:self.HEADER_SIZE]
            
            # Extrair informações do cabeçalho
            self.sample_rate = struct.unpack('H', header[2:4])[0]
            bits_per_sample = struct.unpack('H', header[4:6])[0]
            
            # Validação da taxa de amostragem
            all_common_rates = sorted(set(
                self.exam_params['holter']['common_rates'] + 
                self.exam_params['ecg']['common_rates']
            ))
            
            if self.sample_rate not in all_common_rates:
                if len(self.raw_data) > self.HEADER_SIZE:
                    data_bytes = self.raw_data[self.HEADER_SIZE:]
                    data = np.frombuffer(data_bytes, dtype=np.int16)
                    
                    # Calcular autocorrelação para detectar periodicidade
                    autocorr = np.correlate(data[:10000], data[:10000], mode='full')
                    peaks = np.where(autocorr > np.max(autocorr) * 0.5)[0]
                    if len(peaks) > 1:
                        period = np.diff(peaks)[0]
                        detected_rate = self.sample_rate / period
                        closest_rate = min(all_common_rates, key=lambda x: abs(x - detected_rate))
                        if abs(closest_rate - detected_rate) < 10:
                            self.sample_rate = closest_rate
                        else:
                            self.sample_rate = self.exam_params[self.exam_type]['default_sample_rate']
                    else:
                        self.sample_rate = self.exam_params[self.exam_type]['default_sample_rate']
            
            # Extrair timestamp do cabeçalho
            try:
                timestamp = struct.unpack('I', header[24:28])[0]
                self.start_time = datetime.fromtimestamp(timestamp)
            except:
                self.start_time = datetime.now()
            
            return True
        except Exception as e:
            print(f"Erro ao analisar o cabeçalho: {e}")
            return False

    def extract_annotations(self):
        """Extrai as anotações do arquivo"""
        try:
            # Procurar por anotações no final do arquivo
            end_data = self.raw_data[-2048:]  # Últimos 2048 bytes
            end_shorts = np.frombuffer(end_data, dtype=np.int16)
            
            # Procurar por sequências que possam ser anotações
            for i in range(len(end_shorts) - 3):
                if (end_shorts[i] > 0 and  # Possível timestamp
                    end_shorts[i+1] in self.arrhythmia_codes and  # Possível código
                    end_shorts[i+2] > 0):  # Possível duração
                    
                    annotation = {
                        'sample': end_shorts[i],
                        'type': self.arrhythmia_codes[end_shorts[i+1]],
                        'duration': end_shorts[i+2]
                    }
                    self.annotations.append(annotation)
            
            if self.annotations:
                self.has_annotations = True
                self.has_arrhythmia = any(a['type'] != 'N' for a in self.annotations)
                print(f"Encontradas {len(self.annotations)} anotações")
                print("Tipos de anotações encontrados:", set(a['type'] for a in self.annotations))
            
            return True
        except Exception as e:
            print(f"Erro ao extrair anotações: {e}")
            return False

    def extract_signal_data(self):
        """Extrai os dados do sinal do arquivo"""
        if not self.raw_data:
            return False

        try:
            # Extrair dados após o cabeçalho
            data_bytes = self.raw_data[self.HEADER_SIZE:]
            self.signal_data = np.frombuffer(data_bytes, dtype=np.int16)
            
            # Detectar o tipo de exame
            self.exam_type = self.detect_exam_type(len(self.signal_data), self.sample_rate)
            
            # Validação dos dados
            mean_val = np.mean(self.signal_data)
            std_val = np.std(self.signal_data)
            max_val = np.max(np.abs(self.signal_data))
            
            params = self.exam_params[self.exam_type]
            duration_seconds = len(self.signal_data) / self.sample_rate
            
            # Verificar características típicas
            is_valid = (
                abs(mean_val) < 1000 and
                std_val > params['min_std'] and
                max_val < 32767 and
                duration_seconds >= params['min_duration']
            )
            
            if is_valid:
                self.has_signal_data = True
                print(f"\nDados de {self.exam_type.upper()} detectados:")
                print(f"- Amostras: {len(self.signal_data)}")
                print(f"- Taxa: {self.sample_rate} Hz")
                if self.exam_type == 'holter':
                    print(f"- Duração: {duration_seconds/3600:.2f} horas")
                else:
                    print(f"- Duração: {duration_seconds/60:.2f} minutos")
            else:
                print(f"Aviso: Dados podem não ser de {self.exam_type.upper()}")
            
            return True
        except Exception as e:
            print(f"Erro ao extrair dados: {e}")
            return False

    def convert_to_wfdb(self, output_dir='.'):
        """Converte os dados para o formato WFDB"""
        if not self.has_signal_data:
            return False

        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Normalizar os dados para mV
            signal_mv = self.signal_data * (1.0 / 1000.0)
            
            # Gerar arquivos WFDB
            wfdb.wrsamp(
                record_name=self.record_name,
                fs=self.sample_rate,
                units=['mV'],
                sig_name=[self.exam_type.upper()],
                p_signal=signal_mv.reshape(-1, 1),
                write_dir=output_dir
            )
            
            print(f"\nArquivos WFDB salvos em: {os.path.join(output_dir, self.record_name)}")
            return True
        except Exception as e:
            print(f"Erro ao converter para WFDB: {e}")
            return False

def main():
    converter = HolterConverter("archive/1728654401-4yGR5RuwjImg9MZD.BIN")
    
    if converter.read_bin_file():
        if converter.analyze_header():
            if converter.extract_annotations():
                if converter.extract_signal_data():
                    if converter.convert_to_wfdb("output"):
                        print("\nConversão concluída com sucesso!")

if __name__ == "__main__":
    main() 