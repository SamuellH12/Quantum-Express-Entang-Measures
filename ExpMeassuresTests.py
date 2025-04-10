from circuits.circuitFromFile import * 
from expressibility.meassure import get_KL_divergence
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt


for i in range(1, 20):
    for L in range(1, 2):
        circuito = f'circuits/circuit{i}.descr'
        qc = get_unbound_circuit_from_file(circuito, {'&L':L})
        kl_pq = get_KL_divergence(qc, n_shots=10000, nparams=1000)
        print(f'Circuito {i} | {L} layers | {sum(kl_pq)} KL')
        # print(f'# Circuito {i} | {L} layers\n ```txt')
        # print(qc)
        # print('\n```\n\n')