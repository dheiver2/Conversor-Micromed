import struct
import os
from datetime import datetime

def analyze_bin_file(file_path):
    print(f"Analisando arquivo: {file_path}")
    
    # Obter tamanho do arquivo
    file_size = os.path.getsize(file_path)
    print(f"\nTamanho total do arquivo: {file_size} bytes")
    
    with open(file_path, 'rb') as f:
        # Ler os primeiros bytes do cabeçalho
        header = f.read(32)  # Lendo os primeiros 32 bytes para análise
        
        # Tentar diferentes interpretações dos bytes
        print("\nPossíveis interpretações dos primeiros bytes:")
        
        # Como short (2 bytes)
        shorts = struct.unpack('H' * (len(header)//2), header)
        print(f"\nComo shorts (uint16):")
        for i, val in enumerate(shorts):
            print(f"Bytes {i*2}-{i*2+1}: {val}")
        
        # Como int (4 bytes)
        ints = struct.unpack('I' * (len(header)//4), header)
        print(f"\nComo ints (uint32):")
        for i, val in enumerate(ints):
            print(f"Bytes {i*4}-{i*4+3}: {val}")
        
        # Verificar possível taxa de amostragem
        possible_sample_rate = shorts[0]  # Primeiro short
        print(f"\nPossível taxa de amostragem (primeiro uint16): {possible_sample_rate} Hz")
        
        # Ler alguns dados do meio do arquivo para análise
        f.seek(1024)  # Pular possível cabeçalho
        data_sample = f.read(100)  # Ler 100 bytes de dados
        
        # Analisar dados como shorts (16 bits)
        data_shorts = struct.unpack('h' * (len(data_sample)//2), data_sample)
        print("\nAmostra de dados (como int16):")
        print(data_shorts[:10])  # Mostrar primeiros 10 valores
        
        # Calcular número total de amostras assumindo int16
        possible_samples = (file_size - 1024) // 2
        print(f"\nNúmero possível de amostras (assumindo int16): {possible_samples}")
        
        if possible_sample_rate > 0:
            duration_seconds = possible_samples / possible_sample_rate
            print(f"Duração possível do registro: {duration_seconds:.2f} segundos ({duration_seconds/60:.2f} minutos)")
        
        # Procurar por possíveis anotações no final do arquivo
        f.seek(-1024, 2)  # Ir para os últimos 1024 bytes
        end_data = f.read(1024)
        
        # Tentar identificar padrões que possam indicar anotações
        print("\nAnalisando possíveis anotações no final do arquivo:")
        end_shorts = struct.unpack('H' * (len(end_data)//2), end_data)
        print("Últimos valores (possíveis anotações):")
        print(end_shorts[-20:])  # Mostrar últimos 20 valores

if __name__ == "__main__":
    analyze_bin_file("archive/1728654401-4yGR5RuwjImg9MZD.BIN") 