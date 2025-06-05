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

def save_circuit_image(circuit: QuantumCircuit, file_path: str, style: str = None, ):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    fig = circuit.draw(output='mpl', style=style, fold=50)
    fig.savefig(file_path, bbox_inches='tight', pad_inches=0.1)
    
    plt.close(fig)

import pennylane as qml

def save_pennylane_circuit_image(circuit, n_params, n_qubits, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    qml.drawer.use_style("black_white")
    initial_weights = qml.numpy.random.randn(n_params, requires_grad=True)

    fig, ax = qml.draw_mpl(circuit)(initial_weights, [0]*n_qubits)

    fig.savefig(file_path, bbox_inches="tight")
    plt.close(fig)

# from circuitFromFile import get_unbound_circuit_from_file
# from pennylaneCircuitParse import get_pennylane_circuit_from_file
# for path in get_circuit_path_list('CostaSH'):
#     name = path.split('/')[-1].split('.')[0]
#     folder = path.split('/')[-2]
#     # qc = get_unbound_circuit_from_file(path, {'&L' : 1})
#     # save_circuit_image(qc, f'CostaSH/images/{folder}/{name}.jpg')
#     circuit, dev, n_params = get_pennylane_circuit_from_file(path, {'&L' : 1})
#     save_pennylane_circuit_image(circuit, n_params, int(folder[0]), f'CostaSH/images/pennylane/{folder}/{name}.jpg')
