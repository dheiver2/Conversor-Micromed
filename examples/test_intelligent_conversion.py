import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.converters.holter_converter import HolterConverter, FileType

def test_conversion(bin_file: str, output_dir: str) -> None:
    """
    Testa a conversão inteligente de um arquivo BIN
    
    Args:
        bin_file: Caminho para o arquivo BIN
        output_dir: Diretório de saída
    """
    print(f"\nTestando conversão de: {bin_file}")
    
    # Inicializa o conversor
    converter = HolterConverter(bin_file)
    
    # Analisa o arquivo
    converter.analyze_file_structure()
    
    # Mostra metadados
    print("\nMetadados do arquivo:")
    metadata = converter.get_metadata()
    for key, value in metadata.items():
        print(f"{key}: {value}")
        
    # Mostra quais arquivos serão gerados
    print("\nArquivos que serão gerados:")
    for file_type in converter.required_files:
        print(f"- {file_type.name}")
        
    # Converte para WFDB
    converter.convert_to_wfdb(output_dir)
    
    # Verifica os arquivos gerados
    print("\nArquivos gerados:")
    for file in Path(output_dir).glob(f"{Path(bin_file).stem}.*"):
        print(f"- {file.name}")

def main():
    # Diretórios
    input_dir = "archive"
    output_dir = "output"
    
    # Cria diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Lista todos os arquivos BIN
    bin_files = list(Path(input_dir).glob("*.BIN"))
    
    if not bin_files:
        print("Nenhum arquivo BIN encontrado no diretório de entrada")
        return
        
    # Testa cada arquivo
    for bin_file in bin_files:
        test_conversion(str(bin_file), output_dir)

if __name__ == "__main__":
    main() 