from circuitFromFile import parse_quantum_file 
from circuitFromFile import get_circuit_from_file
from qiskit import QuantumCircuit

_, _, op, np, param = parse_quantum_file('circuit0.descr')

# for x in op:
#     print(x)

# print(np)

seq = [2 for _ in range(np)]

qc = get_circuit_from_file('circuit0.descr', sequenc_params=seq)
print(qc)