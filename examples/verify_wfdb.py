import os
import wfdb
import numpy as np
from pathlib import Path

def verify_wfdb_files(record_path: str) -> None:
    """
    Verifica a qualidade e integridade dos arquivos WFDB gerados
    
    Args:
        record_path: Caminho para o registro WFDB (sem extensão)
    """
    print(f"\nVerificando arquivos WFDB em: {record_path}")
    
    # Verifica arquivo .hea
    try:
        record = wfdb.rdrecord(record_path)
        print("\n✅ Arquivo .hea válido")
        print(f"- Número de sinais: {record.n_sig}")
        print(f"- Taxa de amostragem: {record.fs} Hz")
        print(f"- Número de amostras: {record.sig_len}")
        print(f"- Nomes dos sinais: {record.sig_name}")
        print(f"- Unidades: {record.units}")
    except Exception as e:
        print(f"\n❌ Erro ao ler .hea: {e}")
        
    # Verifica arquivo .dat
    try:
        if os.path.exists(f"{record_path}.dat"):
            print("\n✅ Arquivo .dat encontrado")
            # Verifica se os dados são válidos
            if record.p_signal is not None:
                print(f"- Formato dos dados: {record.p_signal.shape}")
                print(f"- Valor mínimo: {np.min(record.p_signal):.2f} mV")
                print(f"- Valor máximo: {np.max(record.p_signal):.2f} mV")
                print(f"- Valor médio: {np.mean(record.p_signal):.2f} mV")
            else:
                print("❌ Dados não encontrados no arquivo .dat")
        else:
            print("\n❌ Arquivo .dat não encontrado")
    except Exception as e:
        print(f"\n❌ Erro ao verificar .dat: {e}")
        
    # Verifica arquivo .atr
    try:
        if os.path.exists(f"{record_path}.atr"):
            print("\n✅ Arquivo .atr encontrado")
            ann = wfdb.rdann(record_path, 'atr')
            print(f"- Número de anotações: {len(ann.sample)}")
            print(f"- Tipos de anotações: {set(ann.symbol)}")
            print(f"- Primeira anotação: {ann.symbol[0]} em {ann.sample[0]}")
            print(f"- Última anotação: {ann.symbol[-1]} em {ann.sample[-1]}")
        else:
            print("\nℹ️ Arquivo .atr não encontrado")
    except Exception as e:
        print(f"\n❌ Erro ao verificar .atr: {e}")
        
    # Verifica arquivo .ari
    try:
        if os.path.exists(f"{record_path}.ari"):
            print("\n✅ Arquivo .ari encontrado")
            with open(f"{record_path}.ari", 'r') as f:
                arrhythmias = f.readlines()
            print(f"- Número de arritmias: {len(arrhythmias)}")
            print(f"- Primeira arritmia: {arrhythmias[0].strip()}")
            print(f"- Última arritmia: {arrhythmias[-1].strip()}")
        else:
            print("\nℹ️ Arquivo .ari não encontrado")
    except Exception as e:
        print(f"\n❌ Erro ao verificar .ari: {e}")
        
    # Verifica arquivo .qrs
    try:
        if os.path.exists(f"{record_path}.qrs"):
            print("\n✅ Arquivo .qrs encontrado")
            with open(f"{record_path}.qrs", 'r') as f:
                quality_info = f.readlines()
            print("- Informações de qualidade:")
            for line in quality_info:
                print(f"  {line.strip()}")
        else:
            print("\nℹ️ Arquivo .qrs não encontrado")
    except Exception as e:
        print(f"\n❌ Erro ao verificar .qrs: {e}")

def main():
    # Diretório de saída
    output_dir = "output"
    
    # Lista todos os arquivos .hea
    hea_files = list(Path(output_dir).glob("*.hea"))
    
    if not hea_files:
        print("Nenhum arquivo WFDB encontrado no diretório de saída")
        return
        
    # Verifica cada arquivo
    for hea_file in hea_files:
        record_path = str(hea_file.with_suffix(''))
        verify_wfdb_files(record_path)

if __name__ == "__main__":
    main() 