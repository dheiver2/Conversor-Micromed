import struct
import numpy as np
import os
from datetime import datetime

def analyze_bin_structure(file_path):
    print(f"Analisando estrutura do arquivo: {file_path}")
    
    # Obter tamanho do arquivo
    file_size = os.path.getsize(file_path)
    print(f"\nTamanho total do arquivo: {file_size} bytes")
    
    with open(file_path, 'rb') as f:
        # 1. Análise do cabeçalho principal
        print("\n1. Análise do Cabeçalho Principal (primeiros 1024 bytes):")
        header = f.read(1024)
        
        # Tentar diferentes interpretações do cabeçalho
        print("\nPrimeiros 32 bytes como shorts (uint16):")
        header_shorts = struct.unpack('H' * 16, header[:32])
        for i, val in enumerate(header_shorts):
            print(f"Bytes {i*2}-{i*2+1}: {val} (0x{val:04x})")
        
        # Procurar por possíveis flags ou identificadores
        print("\nPossíveis flags no cabeçalho:")
        for i in range(0, 1024, 2):
            val = struct.unpack('H', header[i:i+2])[0]
            if val in [0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040, 0x0080]:
                print(f"Possível flag encontrada em {i}: 0x{val:04x}")
        
        # 2. Análise do final do arquivo (possíveis anotações)
        print("\n2. Análise do Final do Arquivo (últimos 2048 bytes):")
        f.seek(-2048, 2)
        end_data = f.read(2048)
        
        # Converter para diferentes formatos para análise
        end_shorts = np.frombuffer(end_data, dtype=np.int16)
        end_bytes = np.frombuffer(end_data, dtype=np.uint8)
        
        print("\nÚltimos 20 shorts:")
        print(end_shorts[-20:])
        
        print("\nÚltimos 20 bytes (hex):")
        print([f"0x{b:02x}" for b in end_bytes[-20:]])
        
        # Procurar por padrões que possam indicar anotações
        print("\nProcurando por padrões de anotações:")
        unique_values = np.unique(end_shorts)
        print(f"Número de valores únicos: {len(unique_values)}")
        print(f"Valores únicos: {unique_values}")
        
        # 3. Análise de possíveis estruturas de dados
        print("\n3. Análise de Possíveis Estruturas de Dados:")
        
        # Procurar por possíveis timestamps
        print("\nProcurando por possíveis timestamps:")
        for i in range(0, len(header), 4):
            val = struct.unpack('I', header[i:i+4])[0]
            if 946684800 <= val <= 1893456000:  # Valores possíveis de timestamp (2000-2030)
                print(f"Possível timestamp em {i}: {datetime.fromtimestamp(val)}")
        
        # 4. Análise de possíveis códigos de arritmia
        print("\n4. Análise de Possíveis Códigos de Arritmia:")
        
        # Procurar por valores que possam representar códigos de arritmia
        # Valores comuns: 1=N, 2=V, 3=S, 4=F, 5=Q, etc.
        arrhythmia_codes = {1: 'N', 2: 'V', 3: 'S', 4: 'F', 5: 'Q'}
        for i in range(len(end_shorts)):
            if end_shorts[i] in arrhythmia_codes:
                print(f"Possível código de arritmia em {i}: {arrhythmia_codes[end_shorts[i]]}")
        
        # 5. Análise de possíveis estruturas de anotação
        print("\n5. Análise de Possíveis Estruturas de Anotação:")
        
        # Procurar por padrões que possam indicar estruturas de anotação
        # Por exemplo, sequências como [timestamp, código, duração]
        for i in range(len(end_shorts) - 3):
            if (end_shorts[i] > 0 and  # Possível timestamp
                end_shorts[i+1] in arrhythmia_codes and  # Possível código
                end_shorts[i+2] > 0):  # Possível duração
                print(f"Possível estrutura de anotação em {i}:")
                print(f"Timestamp: {end_shorts[i]}")
                print(f"Código: {arrhythmia_codes[end_shorts[i+1]]}")
                print(f"Duração: {end_shorts[i+2]}")

if __name__ == "__main__":
    analyze_bin_structure("archive/1728654401-4yGR5RuwjImg9MZD.BIN") 