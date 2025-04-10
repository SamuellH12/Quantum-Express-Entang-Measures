from circuits.circuitFromFile import parse_quantum_file 
from circuits.circuitFromFile import get_circuit_from_file
from circuits.circuitFromFile import get_unbound_circuit_from_file
from circuits.circuitFromFile import get_circuit_from_desc
from expressibility.meassure import get_KL_divergence
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

# _, _, op, np, param = parse_quantum_file('circuits/circuit1.descr', {'&L':1})
# for x in op: print(x)
# seq = [2 for _ in range(np)]

qc = get_unbound_circuit_from_file('circuits/circuit1.descr', {'&L':1})
print(qc)
qc = get_circuit_from_file('circuits/circuit1.descr', {'&L':1}, [2, 2, 2, 3.14, 2, 2, 2, 2, 2, 2])
print(qc)

# kl_pq = get_KL_divergence(qc, n_shots=10, nparams=20)

# plot_histogram(counts, title='Resultados')    
# plt.savefig('teste.png')