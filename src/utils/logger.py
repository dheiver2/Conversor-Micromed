import logging
import os
from datetime import datetime

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    Configura um logger para o módulo especificado.
    
    Args:
        name: Nome do módulo
        log_dir: Diretório para salvar os logs
        
    Returns:
        Logger configurado
    """
    # Cria diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para arquivo
    log_file = os.path.join(
        log_dir, 
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger 