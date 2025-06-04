import os

def get_files_of_type(root_dir, extension) -> str:
    file_paths = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
                file_paths[-1] = file_paths[-1].replace('\\', '/')
    
    return file_paths

def get_circuit_path_list(path='.') -> str:
    return get_files_of_type(path, '.descr')


from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def save_circuit_image(circuit: QuantumCircuit, file_path: str, dpi: int = 300, style: str = None, ):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    fig = circuit.draw(output='mpl', style=style, fold=50)
    fig.savefig(file_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    
    plt.close(fig)


# from circuitFromFile import get_unbound_circuit_from_file
# for path in get_circuit_path_list('CostaSH'):
#     name = path.split('/')[-1].split('.')[0]
#     folder = path.split('/')[-2]
#     qc = get_unbound_circuit_from_file(path, {'&L' : 1})
#     save_circuit_image(qc, f'CostaSH/images/{folder}/{name}.jpg')