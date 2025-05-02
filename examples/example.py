import os
from src.holter_converter import HolterConverter
from src.visualization import SignalVisualizer

def main():
    # Configura diretórios
    input_dir = "examples/data"
    output_dir = "examples/output"
    plots_dir = "examples/plots"
    
    # Cria diretórios se não existirem
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Inicializa o conversor
    converter = HolterConverter(input_dir, output_dir)
    
    # Converte todos os arquivos do diretório
    print("Convertendo arquivos...")
    converted_files = converter.convert_directory()
    
    if not converted_files:
        print("Nenhum arquivo encontrado para converter.")
        return
    
    print(f"\nArquivos convertidos: {len(converted_files)}")
    
    # Visualiza cada arquivo convertido
    for file_path in converted_files:
        print(f"\nVisualizando {os.path.basename(file_path)}...")
        
        # Inicializa o visualizador
        visualizer = SignalVisualizer(file_path)
        
        # Carrega os dados
        if not visualizer.load_data():
            print(f"Erro ao carregar {file_path}")
            continue
        
        # Gera visualizações
        print("Gerando visualizações...")
        
        # Plota primeiros 10 segundos
        visualizer.plot_signal(0, 10, 
                             save_path=os.path.join(plots_dir, 
                                                  f"{os.path.basename(file_path)}_signal.png"))
        
        # Plota frequência cardíaca
        visualizer.plot_heart_rate(
            save_path=os.path.join(plots_dir, 
                                 f"{os.path.basename(file_path)}_hr.png"))
        
        # Gera resumo completo
        visualizer.plot_summary(plots_dir)
        
        print("Visualizações salvas em:", plots_dir)

if __name__ == "__main__":
    main() 