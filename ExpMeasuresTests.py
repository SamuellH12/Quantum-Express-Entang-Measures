from circuits.circuitFromFile import * 
from expressibility.ExpressMeasure import get_KL_divergence
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt


for i in range(1, 20):
    for L in range(1, 6):
        circuito = f'circuits/circuit{i}.descr'
        qc = get_unbound_circuit_from_file(circuito, {'&L':L})
        kl = get_KL_divergence(qc, n_shots=10000, nparams=1000, reuse_circuit_measures=False)
        print(f'Circuito {i} | {L} layers | {kl} KL')
        # print(f'# Circuito {i} | {L} layers\n ```txt')
        # print(qc)
        # print('\n```\n\n')

# plt.hist(fidelity, bins=b_list)
# plt.savefig('sla.png')
# print('KL(P || Q): %.3f nats' % sum(kl_pq))
# print(P_I_hist)
# print(kl_pq)