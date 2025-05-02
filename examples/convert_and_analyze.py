import os
from src.converters.holter_converter import HolterConverter
from src.analyzers.ecg_analyzer import ECGAnalyzer
from src.visualization.ecg_plotter import ECGPlotter

def main():
    # Diretórios
    input_dir = "archive"
    output_dir = "output"
    bin_file = "1728654401-4yGR5RuwjImg9MZD.BIN"
    
    # Cria diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Converter arquivo BIN para WFDB
    print("Convertendo arquivo BIN para WFDB...")
    converter = HolterConverter(os.path.join(input_dir, bin_file))
    converter.convert_to_wfdb(output_dir)
    
    # 2. Analisar o ECG
    print("\nAnalisando ECG...")
    analyzer = ECGAnalyzer(os.path.join(output_dir, os.path.splitext(bin_file)[0]))
    results = analyzer.analyze()
    
    # Imprime resultados da análise
    print("\nResultados da Análise:")
    print(f"Duração: {results['duration']:.2f} segundos")
    print(f"Taxa de amostragem: {results['sample_rate']} Hz")
    print(f"Número de batimentos: {results['num_beats']}")
    print(f"Qualidade do sinal: {results['signal_quality']['quality']}")
    
    if results['arrhythmias']:
        print("\nArritmias detectadas:")
        for arr in results['arrhythmias']:
            print(f"- {arr['type']} ({arr['severity']})")
    
    # 3. Visualizar resultados
    print("\nGerando visualizações...")
    plotter = ECGPlotter(os.path.join(output_dir, os.path.splitext(bin_file)[0]))
    
    # Plota segmento do ECG
    plotter.plot_segment(start_time=0, duration=10)
    
    # Plota análise de HRV
    plotter.plot_hrv()
    
    # Plota detecção de arritmias
    plotter.plot_arrhythmias()
    
    print("\nProcesso concluído!")
    print(f"Arquivos salvos em: {output_dir}")

if __name__ == "__main__":
    main() 