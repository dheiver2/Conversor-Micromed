import os
import numpy as np
import wfdb
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import struct
from enum import Enum

class FileType(Enum):
    """Tipos de arquivo que podem ser gerados"""
    HEADER = 1
    DATA = 2
    ANNOTATION = 3
    ARRHYTHMIA = 4
    QUALITY = 5

class HolterConverter:
    """Conversor inteligente de arquivos Holter para formato WFDB"""
    
    def __init__(self, bin_file: str):
        """
        Inicializa o conversor com o arquivo BIN de entrada
        
        Args:
            bin_file: Caminho para o arquivo BIN
        """
        self.bin_file = bin_file
        self.raw_data = None
        self.ecg_data = None
        self.annotation_data = None
        self.header = None
        self.sample_rate = None
        self.start_time = None
        self.annotations = []
        self.arrhythmias = []
        self.required_files: Set[FileType] = set()
        self.file_metadata = {}
        
        # Constantes
        self.HEADER_SIZE = 1024
        self.ANNOTATION_SIZE = 1024
        self.DEFAULT_SAMPLE_RATE = 256  # Hz
        self.BYTES_PER_SAMPLE = 2
        
    def read_bin_file(self) -> bool:
        """Lê o arquivo BIN e extrai os dados brutos"""
        try:
            file_size = os.path.getsize(self.bin_file)
            if file_size < self.HEADER_SIZE + self.ANNOTATION_SIZE:
                raise ValueError(f"Arquivo muito pequeno: {file_size} bytes")
                
            with open(self.bin_file, 'rb') as f:
                # Lê o cabeçalho
                self.header = f.read(self.HEADER_SIZE)
                
                # Calcula o tamanho dos dados de ECG
                ecg_data_size = file_size - self.HEADER_SIZE - self.ANNOTATION_SIZE
                if ecg_data_size % self.BYTES_PER_SAMPLE != 0:
                    raise ValueError(f"Tamanho inválido dos dados de ECG: {ecg_data_size} bytes")
                    
                # Lê os dados de ECG
                ecg_bytes = f.read(ecg_data_size)
                self.ecg_data = np.frombuffer(ecg_bytes, dtype=np.int16)
                
                # Lê os dados de anotação
                annotation_bytes = f.read(self.ANNOTATION_SIZE)
                self.annotation_data = np.frombuffer(annotation_bytes, dtype=np.int16)
                
                # Normaliza para mV
                self.ecg_data = self.ecg_data * 0.001  # Assume escala de 1000 unidades/mV
                
                print(f"Arquivo lido com sucesso:")
                print(f"- Tamanho total: {file_size} bytes")
                print(f"- Amostras de ECG: {len(self.ecg_data)}")
                print(f"- Amostras de anotação: {len(self.annotation_data)}")
                return True
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return False
            
    def analyze_file_structure(self) -> None:
        """Analisa a estrutura do arquivo para determinar quais arquivos gerar"""
        # Lê o arquivo
        if not self.read_bin_file():
            raise ValueError("Falha ao ler o arquivo")
            
        # Sempre precisamos de .hea e .dat
        self.required_files.add(FileType.HEADER)
        self.required_files.add(FileType.DATA)
        
        # Verifica se há anotações
        if self._has_annotations(self.annotation_data):
            self.required_files.add(FileType.ANNOTATION)
            self._extract_annotations()
                
        # Verifica se há informações de arritmia
        if self._has_arrhythmia_info(self.header):
            self.required_files.add(FileType.ARRHYTHMIA)
            self._extract_arrhythmias()
            
        # Verifica qualidade do sinal
        if self._has_quality_info(self.header):
            self.required_files.add(FileType.QUALITY)
            
        # Extrai metadados do arquivo
        self._extract_metadata(self.header)
        
    def _has_annotations(self, annotation_data: np.ndarray) -> bool:
        """Verifica se o arquivo contém anotações"""
        if annotation_data is None:
            return False
            
        # Procura por padrões de anotação
        unique_values = np.unique(annotation_data)
        if len(unique_values) > 10:  # Se houver muitos valores únicos, provavelmente são anotações
            return True
        return False
        
    def _extract_annotations(self) -> None:
        """Extrai anotações dos dados"""
        if self.annotation_data is None:
            return
            
        # Procura por padrões de anotação
        for i in range(0, len(self.annotation_data), 2):
            if i + 1 >= len(self.annotation_data):
                break
                
            # Verifica se é um marcador de anotação
            if self.annotation_data[i] != 0:
                self.annotations.append((
                    self.annotation_data[i],  # Posição
                    chr(self.annotation_data[i + 1] & 0xFF)  # Tipo
                ))
                
    def _extract_arrhythmias(self) -> None:
        """Extrai informações de arritmia do cabeçalho"""
        arrhythmia_codes = {
            1: 'N',  # Normal
            2: 'V',  # Ventricular
            3: 'S',  # Supraventricular
            4: 'F',  # Fibrilação
            5: 'Q'   # Pausa/QRS não detectado
        }
        
        # Procura por códigos de arritmia no cabeçalho
        for i in range(0, len(self.header), 2):
            if i + 1 >= len(self.header):
                break
                
            code = int.from_bytes(self.header[i:i+2], byteorder='little')
            if code in arrhythmia_codes:
                self.arrhythmias.append({
                    'start': i,
                    'type': arrhythmia_codes[code],
                    'severity': 'moderate'  # Default
                })
                
    def _has_arrhythmia_info(self, header_bytes: bytes) -> bool:
        """Verifica se o arquivo contém informações de arritmia"""
        arrhythmia_codes = [1, 2, 3, 4, 5]
        for code in arrhythmia_codes:
            if struct.pack('H', code) in header_bytes:
                return True
        return False
        
    def _has_quality_info(self, header_bytes: bytes) -> bool:
        """Verifica se o arquivo contém informações de qualidade"""
        quality_flags = [0x01, 0x02, 0x04, 0x08]
        for flag in quality_flags:
            if struct.pack('B', flag) in header_bytes:
                return True
        return False
        
    def _extract_metadata(self, header_bytes: bytes) -> None:
        """Extrai metadados do arquivo"""
        try:
            # Tenta extrair taxa de amostragem do cabeçalho
            self.sample_rate = int.from_bytes(header_bytes[2:4], byteorder='little')
            
            # Valida a taxa de amostragem
            if self.sample_rate < 100 or self.sample_rate > 1000:
                print(f"Taxa de amostragem inválida ({self.sample_rate}), usando padrão: {self.DEFAULT_SAMPLE_RATE}")
                self.sample_rate = self.DEFAULT_SAMPLE_RATE
                
            # Tenta extrair timestamp
            try:
                timestamp_bytes = header_bytes[24:28]
                self.start_time = datetime.fromtimestamp(
                    int.from_bytes(timestamp_bytes, byteorder='little')
                )
            except:
                self.start_time = datetime.now()
                
            # Armazena metadados
            self.file_metadata = {
                'sample_rate': self.sample_rate,
                'start_time': self.start_time,
                'file_size': os.path.getsize(self.bin_file),
                'num_samples': len(self.ecg_data) if self.ecg_data is not None else 0,
                'duration_seconds': len(self.ecg_data) / self.sample_rate if self.ecg_data is not None else 0,
                'num_annotations': len(self.annotations),
                'num_arrhythmias': len(self.arrhythmias),
                'has_annotations': FileType.ANNOTATION in self.required_files,
                'has_arrhythmia': FileType.ARRHYTHMIA in self.required_files,
                'has_quality': FileType.QUALITY in self.required_files
            }
        except Exception as e:
            print(f"Erro ao extrair metadados: {e}")
            raise
            
    def convert_to_wfdb(self, output_dir: str) -> None:
        """
        Converte o arquivo BIN para formato WFDB, gerando apenas os arquivos necessários
        
        Args:
            output_dir: Diretório de saída para os arquivos WFDB
        """
        if self.ecg_data is None:
            raise ValueError("Dados de ECG não disponíveis")
            
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome base do arquivo
        base_name = os.path.splitext(os.path.basename(self.bin_file))[0]
        
        try:
            # Gera arquivos necessários
            if FileType.HEADER in self.required_files or FileType.DATA in self.required_files:
                print("Gerando arquivos .hea e .dat...")
                # Garante que os dados estão no formato correto
                signal = self.ecg_data.reshape(-1, 1)
                
                # Gera o arquivo WFDB
                wfdb.wrsamp(
                    record_name=base_name,
                    fs=self.sample_rate,
                    units=['mV'],
                    sig_name=['ECG'],
                    p_signal=signal,
                    write_dir=output_dir,
                    comments=['Converted from Holter BIN file']
                )
                
            if FileType.ANNOTATION in self.required_files and self.annotations:
                print("Gerando arquivo .atr...")
                # Converte as anotações para o formato WFDB
                sample = np.array([a[0] for a in self.annotations])
                symbol = [a[1] for a in self.annotations]
                
                # Gera o arquivo de anotação
                wfdb.wrann(
                    record_name=base_name,
                    extension='atr',
                    sample=sample,
                    symbol=symbol,
                    fs=self.sample_rate,
                    write_dir=output_dir
                )
                
            if FileType.ARRHYTHMIA in self.required_files and self.arrhythmias:
                print("Gerando arquivo .ari...")
                with open(os.path.join(output_dir, f"{base_name}.ari"), 'w') as f:
                    for arr in self.arrhythmias:
                        f.write(f"{arr['start']} {arr['type']} {arr['severity']}\n")
                        
            if FileType.QUALITY in self.required_files:
                print("Gerando arquivo .qrs...")
                with open(os.path.join(output_dir, f"{base_name}.qrs"), 'w') as f:
                    f.write(f"Sample Rate: {self.sample_rate}\n")
                    f.write(f"Start Time: {self.start_time}\n")
                    f.write(f"File Size: {self.file_metadata['file_size']}\n")
                    f.write(f"Number of Samples: {self.file_metadata['num_samples']}\n")
                    f.write(f"Duration (seconds): {self.file_metadata['duration_seconds']:.2f}\n")
                    f.write(f"Number of Annotations: {self.file_metadata['num_annotations']}\n")
                    f.write(f"Number of Arrhythmias: {self.file_metadata['num_arrhythmias']}\n")
                    f.write(f"Has Annotations: {self.file_metadata['has_annotations']}\n")
                    f.write(f"Has Arrhythmia: {self.file_metadata['has_arrhythmia']}\n")
                    f.write(f"Has Quality Info: {self.file_metadata['has_quality']}\n")
                    
            print(f"\nConversão concluída. Arquivos gerados em {output_dir}:")
            for file_type in self.required_files:
                print(f"- {file_type.name}")
                
        except Exception as e:
            print(f"Erro durante a conversão: {e}")
            raise
            
    def get_metadata(self) -> Dict:
        """Retorna metadados do arquivo"""
        return self.file_metadata 