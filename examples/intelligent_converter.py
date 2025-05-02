import os
from src.converters.holter_converter import HolterConverter, FileType

def main():
    # Diretórios
    input_dir = "archive"
    output_dir = "output"
    bin_file = "1728654401-4yGR5RuwjImg9MZD.BIN"
    
    # Cria diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializa o conversor
    print("Inicializando conversor inteligente...")
    converter = HolterConverter(os.path.join(input_dir, bin_file))
    
    # Analisa o arquivo e determina quais arquivos gerar
    print("\nAnalisando estrutura do arquivo...")
    converter.analyze_file_structure()
    
    # Mostra quais arquivos serão gerados
    print("\nArquivos que serão gerados:")
    for file_type in converter.required_files:
        print(f"- {file_type.name}")
        
    # Mostra metadados do arquivo
    print("\nMetadados do arquivo:")
    metadata = converter.get_metadata()
    for key, value in metadata.items():
        print(f"{key}: {value}")
        
    # Converte o arquivo
    print("\nConvertendo arquivo...")
    converter.convert_to_wfdb(output_dir)
    
    print("\nProcesso concluído!")
    print(f"Arquivos salvos em: {output_dir}")

if __name__ == "__main__":
    main() 