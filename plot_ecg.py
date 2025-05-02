import wfdb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import os

def plot_ecg(record_name, output_dir='output', duration=10, start_time=0):
    """
    Plota o ECG no formato padrão médico
    
    Args:
        record_name: Nome do registro WFDB
        output_dir: Diretório onde estão os arquivos
        duration: Duração do segmento a ser plotado em segundos
        start_time: Tempo inicial em segundos
    """
    try:
        # Ler o registro WFDB
        record = wfdb.rdrecord(os.path.join(output_dir, record_name))
        
        # Calcular número de amostras para o segmento
        fs = record.fs
        start_sample = int(start_time * fs)
        num_samples = int(duration * fs)
        
        # Extrair os dados do ECG
        ecg_data = record.p_signal[start_sample:start_sample + num_samples, 0]
        
        # Criar figura com grade
        fig = plt.figure(figsize=(20, 10))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        # Configurar o eixo x (tempo)
        time = np.arange(len(ecg_data)) / fs
        ax.plot(time, ecg_data, 'k-', linewidth=0.5)
        
        # Configurar a grade
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xticks(np.arange(0, duration, 0.2))  # Linhas verticais a cada 0.2s
        ax.set_yticks(np.arange(-2, 2, 0.5))  # Linhas horizontais a cada 0.5mV
        
        # Configurar os eixos
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Amplitude (mV)')
        ax.set_title(f'ECG - {record_name}')
        
        # Adicionar escala
        # Linha horizontal de 1mV
        ax.plot([duration-1, duration], [1, 1], 'k-', linewidth=2)
        # Linha vertical de 0.2s
        ax.plot([duration-0.2, duration], [1.5, 1.5], 'k-', linewidth=2)
        ax.text(duration-0.5, 1, '1 mV', ha='right')
        ax.text(duration-0.1, 1.5, '0.2 s', ha='right')
        
        # Ajustar limites
        ax.set_xlim(0, duration)
        ax.set_ylim(-2, 2)
        
        # Tentar ler e plotar anotações se existirem
        try:
            ann = wfdb.rdann(os.path.join(output_dir, record_name), 'atr')
            for i, (sample, symbol) in enumerate(zip(ann.sample, ann.symbol)):
                if start_sample <= sample < start_sample + num_samples:
                    time_ann = (sample - start_sample) / fs
                    ax.plot([time_ann], [ecg_data[sample - start_sample]], 'ro', markersize=4)
                    ax.text(time_ann, ecg_data[sample - start_sample] + 0.2, symbol,
                           ha='center', color='red')
        except:
            print("Não foi possível carregar anotações")
        
        # Salvar o gráfico
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{record_name}_ecg.png"), dpi=300)
        plt.close()
        
        print(f"Gráfico salvo em: {os.path.join(output_dir, f'{record_name}_ecg.png')}")
        
    except Exception as e:
        print(f"Erro ao plotar ECG: {e}")

def main():
    # Exemplo de uso
    record_name = "1728654401-4yGR5RuwjImg9MZD"
    plot_ecg(record_name, duration=10)  # Plota 10 segundos do ECG

if __name__ == "__main__":
    main() 