import os
import numpy as np
import wfdb
from datetime import datetime
import logging
from typing import Optional, Tuple, Dict, List
import json

class HolterConverter:
    def __init__(self, input_dir: str, output_dir: str):
        """Inicializa o conversor de Holter/ECG
        
        Args:
            input_dir (str): Diretório de entrada com arquivos .dat
            output_dir (str): Diretório de saída para arquivos WFDB
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.sample_rate = None
        self.exam_type = None
        self.metadata = {}
        
        # Configura logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('converter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _validate_input(self, dat_file: str) -> bool:
        """Valida o arquivo de entrada
        
        Args:
            dat_file (str): Caminho do arquivo .dat
            
        Returns:
            bool: True se o arquivo é válido
        """
        if not os.path.exists(dat_file):
            self.logger.error(f"Arquivo não encontrado: {dat_file}")
            return False
            
        if not dat_file.endswith('.dat'):
            self.logger.error(f"Arquivo deve ter extensão .dat: {dat_file}")
            return False
            
        return True
    
    def _detect_sample_rate(self, data: np.ndarray) -> int:
        """Detecta a taxa de amostragem do sinal
        
        Args:
            data (np.ndarray): Dados do sinal
            
        Returns:
            int: Taxa de amostragem detectada
        """
        # Lista de taxas de amostragem comuns
        common_rates = [128, 250, 500, 1000]
        
        # Calcula duração em segundos
        duration = len(data) / max(common_rates)
        
        # Se duração > 1 hora, provavelmente é Holter
        if duration > 3600:
            self.exam_type = 'holter'
            # Holter geralmente usa 128 Hz
            return 128
        else:
            self.exam_type = 'ecg'
            # ECG geralmente usa 500 Hz
            return 500
    
    def _process_signal(self, data: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Processa o sinal e extrai metadados
        
        Args:
            data (np.ndarray): Dados brutos do sinal
            
        Returns:
            Tuple[np.ndarray, Dict]: Dados processados e metadados
        """
        # Detecta taxa de amostragem
        self.sample_rate = self._detect_sample_rate(data)
        
        # Calcula estatísticas
        stats = {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'duration': len(data) / self.sample_rate
        }
        
        # Normaliza dados
        processed_data = (data - stats['mean']) / stats['std']
        
        return processed_data, stats
    
    def convert_file(self, dat_file: str) -> Optional[str]:
        """Converte um arquivo .dat para formato WFDB
        
        Args:
            dat_file (str): Nome do arquivo .dat
            
        Returns:
            Optional[str]: Nome do arquivo convertido ou None em caso de erro
        """
        try:
            # Valida entrada
            if not self._validate_input(dat_file):
                return None
                
            self.logger.info(f"Processando arquivo: {dat_file}")
            
            # Lê dados
            data = np.fromfile(dat_file, dtype=np.int16)
            
            # Processa sinal
            processed_data, stats = self._process_signal(data)
            
            # Cria nome do arquivo de saída
            base_name = os.path.splitext(os.path.basename(dat_file))[0]
            output_file = os.path.join(self.output_dir, base_name)
            
            # Salva metadados
            self.metadata[base_name] = {
                'exam_type': self.exam_type,
                'sample_rate': self.sample_rate,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cria registro WFDB
            record = wfdb.Record(
                record_name=base_name,
                p_signal=processed_data.reshape(-1, 1),
                fs=self.sample_rate,
                sig_name=['ECG'],
                units=['mV'],
                comments=[f'Converted from {dat_file}']
            )
            
            # Salva arquivo
            wfdb.wrsamp(record, write_dir=self.output_dir)
            
            self.logger.info(f"Arquivo convertido com sucesso: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erro ao converter {dat_file}: {str(e)}")
            return None
    
    def convert_directory(self) -> List[str]:
        """Converte todos os arquivos .dat no diretório de entrada
        
        Returns:
            List[str]: Lista de arquivos convertidos com sucesso
        """
        converted_files = []
        
        # Cria diretório de saída se não existir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Lista arquivos .dat
        dat_files = [f for f in os.listdir(self.input_dir) if f.endswith('.dat')]
        
        if not dat_files:
            self.logger.warning(f"Nenhum arquivo .dat encontrado em {self.input_dir}")
            return converted_files
            
        # Converte cada arquivo
        for dat_file in dat_files:
            input_path = os.path.join(self.input_dir, dat_file)
            output_file = self.convert_file(input_path)
            if output_file:
                converted_files.append(output_file)
        
        # Salva metadados
        self._save_metadata()
        
        return converted_files
    
    def _save_metadata(self):
        """Salva metadados em arquivo JSON"""
        metadata_file = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)
        self.logger.info(f"Metadados salvos em: {metadata_file}")
    
    def get_metadata(self) -> Dict:
        """Retorna metadados dos arquivos convertidos
        
        Returns:
            Dict: Dicionário com metadados
        """
        return self.metadata 