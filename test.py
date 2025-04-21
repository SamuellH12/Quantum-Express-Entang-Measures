from circuits.circuitFromFile import parse_quantum_file 
from circuits.circuitFromFile import get_circuit_from_file
from circuits.circuitFromFile import get_unbound_circuit_from_file
from circuits.circuitFromFile import get_circuit_from_desc
from circuits.CustomUnitary.unitary import get_model_unitary
from expressibility.ExpressMeasure import get_KL_divergence
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
import math
import numpy as np


n_features = 2
iqc_gate = get_model_unitary('IQC', n_features)

params = {p : np.random.random() for p in iqc_gate.params}
bound_gate = iqc_gate.assign_parameters(params, False)
unitary_matrix = bound_gate.to_matrix()
print(unitary_matrix)


# # a o circuito com os parâmetros fornecidos qc,_,_ = circuit_model(data=tx[0],w=tw,counter=counter,qubits=qubits,N_qubits=N_qubits,N_features=NF,model=MODEL,folder=folder,N_qubits_tgt=None,N_layers=None)
NF=2
gate =  get_model_unitary('IQC', N_features=NF)

qc = get_unbound_circuit_from_file('circuits/CustomUnitary/circuitUni.descr', custom_gates={'gate' : gate})
print(qc)

qasm_simulator = Aer.get_backend("qasm_simulator")
kl_pq = get_KL_divergence(qc, n_shots=10000, nparams=5000, backend=qasm_simulator, reuse_circuit_measures=True)

