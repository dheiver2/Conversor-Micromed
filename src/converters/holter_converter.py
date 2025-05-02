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
        self.header = None
        self.sample_rate = None
        self.start_time = None
        self.annotations = []
        self.arrhythmias = []
        self.required_files: Set[FileType] = set()
        self.file_metadata = {}
        
    def analyze_file_structure(self) -> None:
        """Analisa a estrutura do arquivo para determinar quais arquivos gerar"""
        # Lê o arquivo inteiro
        with open(self.bin_file, 'rb') as f:
            file_size = os.path.getsize(self.bin_file)
            data = f.read()
            
        # Sempre precisamos de .hea e .dat
        self.required_files.add(FileType.HEADER)
        self.required_files.add(FileType.DATA)
        
        # Analisa o cabeçalho
        header_bytes = data[:1024]
        
        # Verifica se há anotações (últimos 1024 bytes)
        annotation_bytes = data[-1024:]
        if self._has_annotations(annotation_bytes):
            self.required_files.add(FileType.ANNOTATION)
            
        # Verifica se há informações de arritmia
        if self._has_arrhythmia_info(header_bytes):
            self.required_files.add(FileType.ARRHYTHMIA)
            
        # Verifica qualidade do sinal
        if self._has_quality_info(header_bytes):
            self.required_files.add(FileType.QUALITY)
            
        # Extrai metadados do arquivo
        self._extract_metadata(header_bytes)
        
    def _has_annotations(self, annotation_bytes: bytes) -> bool:
        """Verifica se o arquivo contém anotações"""
        # Converte para shorts
        shorts = np.frombuffer(annotation_bytes, dtype=np.int16)
        
        # Procura por padrões de anotação
        # Um padrão comum é ter valores específicos seguidos de timestamps
        unique_values = np.unique(shorts)
        if len(unique_values) > 10:  # Se houver muitos valores únicos, provavelmente são anotações
            return True
            
        return False
        
    def _has_arrhythmia_info(self, header_bytes: bytes) -> bool:
        """Verifica se o arquivo contém informações de arritmia"""
        # Procura por códigos de arritmia no cabeçalho
        arrhythmia_codes = {
            1: 'N',  # Normal
            2: 'V',  # Ventricular
            3: 'S',  # Supraventricular
            4: 'F',  # Fibrilação
            5: 'Q'   # Pausa/QRS não detectado
        }
        
        # Verifica se há referências a esses códigos
        for code in arrhythmia_codes.keys():
            if struct.pack('H', code) in header_bytes:
                return True
                
        return False
        
    def _has_quality_info(self, header_bytes: bytes) -> bool:
        """Verifica se o arquivo contém informações de qualidade"""
        # Procura por flags de qualidade no cabeçalho
        quality_flags = [0x01, 0x02, 0x04, 0x08]  # Exemplos de flags de qualidade
        for flag in quality_flags:
            if struct.pack('B', flag) in header_bytes:
                return True
                
        return False
        
    def _extract_metadata(self, header_bytes: bytes) -> None:
        """Extrai metadados do arquivo"""
        # Extrai taxa de amostragem
        self.sample_rate = int.from_bytes(header_bytes[:4], byteorder='little')
        
        # Extrai timestamp
        try:
            timestamp_bytes = header_bytes[24:32]
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
            'has_annotations': FileType.ANNOTATION in self.required_files,
            'has_arrhythmia': FileType.ARRHYTHMIA in self.required_files,
            'has_quality': FileType.QUALITY in self.required_files
        }
        
    def convert_to_wfdb(self, output_dir: str) -> None:
        """
        Converte o arquivo BIN para formato WFDB, gerando apenas os arquivos necessários
        
        Args:
            output_dir: Diretório de saída para os arquivos WFDB
        """
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Analisa a estrutura do arquivo
        self.analyze_file_structure()
        
        # Nome base do arquivo
        base_name = os.path.splitext(os.path.basename(self.bin_file))[0]
        
        # Gera arquivos necessários
        if FileType.HEADER in self.required_files:
            self._generate_header_file(base_name, output_dir)
            
        if FileType.DATA in self.required_files:
            self._generate_data_file(base_name, output_dir)
            
        if FileType.ANNOTATION in self.required_files:
            self._generate_annotation_file(base_name, output_dir)
            
        if FileType.ARRHYTHMIA in self.required_files:
            self._generate_arrhythmia_file(base_name, output_dir)
            
        if FileType.QUALITY in self.required_files:
            self._generate_quality_file(base_name, output_dir)
            
        print(f"Conversão concluída. Arquivos gerados em {output_dir}:")
        for file_type in self.required_files:
            print(f"- {file_type.name}")
            
    def _generate_header_file(self, base_name: str, output_dir: str) -> None:
        """Gera arquivo .hea"""
        header = wfdb.Record(
            record_name=base_name,
            n_sig=1,
            fs=self.sample_rate,
            sig_len=len(self.raw_data) if self.raw_data is not None else 0,
            base_date=self.start_time.date(),
            base_time=self.start_time.time(),
            sig_name=['ECG'],
            units=['mV'],
            comments=['Converted from Holter BIN file']
        )
        
        wfdb.wrsamp(
            record_name=base_name,
            fs=self.sample_rate,
            units=['mV'],
            sig_name=['ECG'],
            p_signal=self.raw_data.reshape(-1, 1) if self.raw_data is not None else None,
            write_dir=output_dir
        )
        
    def _generate_data_file(self, base_name: str, output_dir: str) -> None:
        """Gera arquivo .dat"""
        # O arquivo .dat é gerado automaticamente pelo wfdb.wrsamp
        pass
        
    def _generate_annotation_file(self, base_name: str, output_dir: str) -> None:
        """Gera arquivo .atr"""
        if self.annotations:
            ann = wfdb.Annotation(
                record_name=base_name,
                sample=self.annotations,
                symbol=[a[1] for a in self.annotations],
                aux_note=None,
                fs=self.sample_rate
            )
            wfdb.wrann(ann, write_dir=output_dir)
            
    def _generate_arrhythmia_file(self, base_name: str, output_dir: str) -> None:
        """Gera arquivo .ari"""
        if self.arrhythmias:
            # Cria arquivo de arritmia personalizado
            with open(os.path.join(output_dir, f"{base_name}.ari"), 'w') as f:
                for arr in self.arrhythmias:
                    f.write(f"{arr['start']} {arr['type']} {arr['severity']}\n")
                    
    def _generate_quality_file(self, base_name: str, output_dir: str) -> None:
        """Gera arquivo .qrs"""
        # Cria arquivo de qualidade personalizado
        with open(os.path.join(output_dir, f"{base_name}.qrs"), 'w') as f:
            f.write(f"Sample Rate: {self.sample_rate}\n")
            f.write(f"Start Time: {self.start_time}\n")
            f.write(f"File Size: {self.file_metadata['file_size']}\n")
            f.write(f"Has Annotations: {self.file_metadata['has_annotations']}\n")
            f.write(f"Has Arrhythmia: {self.file_metadata['has_arrhythmia']}\n")
            f.write(f"Has Quality Info: {self.file_metadata['has_quality']}\n")
            
    def get_metadata(self) -> Dict:
        """Retorna metadados do arquivo"""
        return self.file_metadata 