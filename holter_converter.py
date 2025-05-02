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
        self.ecg_data = None
        self.record_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Constantes do formato do arquivo
        self.HEADER_SIZE = 1024
        self.BYTES_PER_SAMPLE = 2
        self.DEFAULT_SAMPLE_RATE = 256  # Hz
        
        # Flags para determinar quais arquivos gerar
        self.has_ecg_data = False
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

    def read_bin_file(self):
        """Lê o arquivo BIN e extrai os dados brutos"""
        try:
            with open(self.file_path, 'rb') as file:
                self.raw_data = file.read()
            print(f"Arquivo lido com sucesso. Tamanho: {len(self.raw_data)} bytes")
            return True
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return False

    def analyze_header(self):
        """Analisa o cabeçalho do arquivo para extrair informações importantes"""
        if not self.raw_data:
            print("Dados não carregados. Por favor, leia o arquivo primeiro.")
            return False

        try:
            header = self.raw_data[:self.HEADER_SIZE]
            
            # Extrair informações do cabeçalho
            format_id = struct.unpack('H', header[0:2])[0]  # Identificador do formato
            self.sample_rate = struct.unpack('H', header[2:4])[0]  # Taxa de amostragem
            bits_per_sample = struct.unpack('H', header[4:6])[0]  # Bits por amostra
            
            print(f"Identificador do formato: {format_id}")
            print(f"Taxa de amostragem: {self.sample_rate} Hz")
            print(f"Bits por amostra: {bits_per_sample}")
            
            # Se a taxa de amostragem parecer inválida, usar o valor padrão
            if self.sample_rate < 100 or self.sample_rate > 1000:
                print(f"Taxa de amostragem inválida ({self.sample_rate}), usando padrão: {self.DEFAULT_SAMPLE_RATE}")
                self.sample_rate = self.DEFAULT_SAMPLE_RATE
            
            # Extrair timestamp do cabeçalho
            try:
                timestamp = struct.unpack('I', header[24:28])[0]
                self.start_time = datetime.fromtimestamp(timestamp)
                print(f"Data/hora do exame: {self.start_time}")
            except:
                print("Não foi possível extrair timestamp do cabeçalho")
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

    def extract_ecg_data(self):
        """Extrai os dados de ECG do arquivo"""
        if not self.raw_data:
            print("Dados não carregados. Por favor, leia o arquivo primeiro.")
            return False

        try:
            # Extrair dados após o cabeçalho
            data_bytes = self.raw_data[self.HEADER_SIZE:]
            
            # Converter bytes para array de int16 (2 bytes por amostra)
            self.ecg_data = np.frombuffer(data_bytes, dtype=np.int16)
            
            # Verificar se os dados parecem ser de ECG
            mean_val = np.mean(self.ecg_data)
            std_val = np.std(self.ecg_data)
            
            if abs(mean_val) < 1000 and std_val > 100:  # Valores típicos de ECG
                self.has_ecg_data = True
                print("Dados de ECG detectados com sucesso")
            else:
                print("Aviso: Os dados podem não ser de ECG")
            
            # Calcular duração do registro
            duration_seconds = len(self.ecg_data) / self.sample_rate
            print(f"Número de amostras: {len(self.ecg_data)}")
            print(f"Duração: {duration_seconds:.2f} segundos ({duration_seconds/60:.2f} minutos)")
            
            return True
        except Exception as e:
            print(f"Erro ao extrair dados de ECG: {e}")
            return False

    def convert_to_wfdb(self, output_dir='.'):
        """Converte os dados para o formato WFDB, gerando os arquivos necessários"""
        if not self.has_ecg_data:
            print("Dados de ECG não disponíveis. Por favor, extraia os dados primeiro.")
            return False

        try:
            # Criar o diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Normalizar os dados para mV
            ecg_mv = self.ecg_data * (1.0 / 1000.0)
            
            # Configurar os metadados do sinal
            signal_metadata = {
                'fs': self.sample_rate,
                'sig_name': ['ECG'],
                'units': ['mV'],
                'comments': [f'Converted from {self.file_path}'],
                'base_time': self.start_time.strftime('%H:%M:%S'),
                'base_date': self.start_time.strftime('%d/%m/%Y')
            }
            
            # Gerar arquivos WFDB
            print("\nGerando arquivos WFDB:")
            
            # 1. Arquivos básicos (.hea e .dat)
            print("- Gerando arquivos .hea e .dat")
            wfdb.wrsamp(
                record_name=self.record_name,
                fs=self.sample_rate,
                units=['mV'],
                sig_name=['ECG'],
                p_signal=ecg_mv.reshape(-1, 1),
                write_dir=output_dir
            )
            
            # 2. Arquivo de anotações (.atr) se necessário
            if self.has_annotations:
                print("- Gerando arquivo .atr")
                # Criar anotações no formato WFDB
                wfdb_annotations = []
                for ann in self.annotations:
                    wfdb_annotations.append(wfdb.Annotation(
                        sample=ann['sample'],
                        symbol=ann['type'],
                        aux_note=f"Duration: {ann['duration']} samples"
                    ))
                
                # Salvar anotações
                wfdb.wrann(
                    record_name=self.record_name,
                    extension='atr',
                    sample=wfdb_annotations,
                    write_dir=output_dir
                )
            
            # 3. Arquivo de arritmia (.ari) se necessário
            if self.has_arrhythmia:
                print("- Gerando arquivo .ari")
                # Criar arquivo de arritmia
                arrhythmia_events = []
                for ann in self.annotations:
                    if ann['type'] != 'N':  # Apenas eventos não normais
                        arrhythmia_events.append({
                            'type': ann['type'],
                            'start': ann['sample'],
                            'duration': ann['duration']
                        })
                
                # Salvar informações de arritmia
                with open(os.path.join(output_dir, f"{self.record_name}.ari"), 'w') as f:
                    for event in arrhythmia_events:
                        f.write(f"{event['type']} {event['start']} {event['duration']}\n")
            
            print(f"\nArquivos WFDB salvos em: {os.path.join(output_dir, self.record_name)}")
            return True
        except Exception as e:
            print(f"Erro ao converter para formato WFDB: {e}")
            return False

def main():
    # Exemplo de uso
    converter = HolterConverter("archive/1728654401-4yGR5RuwjImg9MZD.BIN")
    
    if converter.read_bin_file():
        print("\nAnalisando cabeçalho...")
        if converter.analyze_header():
            print("\nExtraindo anotações...")
            if converter.extract_annotations():
                print("\nExtraindo dados de ECG...")
                if converter.extract_ecg_data():
                    print("\nConvertendo para WFDB...")
                    if converter.convert_to_wfdb("output"):
                        print("\nProcesso de conversão concluído com sucesso!")

if __name__ == "__main__":
    main() 