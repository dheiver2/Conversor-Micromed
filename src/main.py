import os
import sys
from holter_converter import HolterConverter
from visualization import SignalVisualizer

def process_file(input_file, output_dir='output', plot_dir='plots'):
    """Processa um arquivo de entrada, converte e gera visualizações"""
    # Cria diretórios se necessário
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)
    
    # Converte o arquivo
    print(f"\nProcessando arquivo: {input_file}")
    converter = HolterConverter(input_file)
    
    if converter.read_bin_file():
        if converter.analyze_header():
            if converter.extract_signal_data():
                if converter.convert_to_wfdb(output_dir):
                    print("Conversão concluída com sucesso!")
                    
                    # Gera visualizações
                    print("\nGerando visualizações...")
                    record_path = os.path.join(output_dir, converter.record_name)
                    visualizer = SignalVisualizer(record_path)
                    
                    if visualizer.load_data():
                        # Gera resumo visual
                        visualizer.plot_summary(plot_dir)
                        print(f"Visualizações salvas em: {plot_dir}")
                    else:
                        print("Erro ao gerar visualizações")
                else:
                    print("Erro na conversão para WFDB")
            else:
                print("Erro ao extrair dados do sinal")
        else:
            print("Erro ao analisar cabeçalho")
    else:
        print("Erro ao ler arquivo")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_entrada> [diretorio_saida] [diretorio_plots]")
        return
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    plot_dir = sys.argv[3] if len(sys.argv) > 3 else 'plots'
    
    process_file(input_file, output_dir, plot_dir)

if __name__ == "__main__":
    main() 