from circuits.circuitFromFile import * 
from expressibility.ExpressMeasure import get_KL_divergence
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from circuits.listCircuits import get_circuit_path_list

print('| Qubits | name | Layers | KL divergence')
print('|:-------|:-----|:-------|:------------- ')

for path in get_circuit_path_list('./circuits/CostaSH/'):    
    qc = get_unbound_circuit_from_file(path, {'&L':1})
    kl = get_KL_divergence(qc, n_shots=10000, nparams=1000, reuse_circuit_measures=False)

    # nomes e formatação
    qubits, name = path.split('/')[-2:]
    if qubits[-1] != 's': qubits += 's'
    name = name.split('.')[0]
    name += (' '*(10-len(name)))
    ###

    print(f'{qubits} | {name}| {1} layers | {kl:.10f} KL')


# for i in range(1, 20):
#     for L in range(1, 6):
#         circuito = f'circuits/circuit{i}.descr'
#         qc = get_unbound_circuit_from_file(circuito, {'&L':L})
#         kl = get_KL_divergence(qc, n_shots=10000, nparams=1000, reuse_circuit_measures=False)
#         print(f'Circuito {i} | {L} layers | {kl} KL')

# plt.hist(fidelity, bins=b_list)
# plt.savefig('sla.png')
# print('KL(P || Q): %.3f nats' % sum(kl_pq))
# print(P_I_hist)
# print(kl_pq)