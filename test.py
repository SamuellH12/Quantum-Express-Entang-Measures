# from circuits.circuitFromFile import parse_quantum_file 
# from circuits.circuitFromFile import get_circuit_from_file
# from circuits.circuitFromFile import get_unbound_circuit_from_file
# from circuits.circuitFromFile import get_circuit_from_desc
# from circuits.CustomUnitary.unitary import get_model_unitary
# from expressibility.ExpressMeasure import get_KL_divergence
# from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
# from qiskit.visualization import plot_histogram
# from qiskit_aer import Aer
# import math
# import numpy as np
from pennylane import numpy as np


from qmlHelper.dataPlots import print2D_decision_region
from circuits.pennylaneCircuitParse import get_pennylane_circuit_from_file

from sklearn import preprocessing
from sklearn.datasets import make_blobs
MAXVALUERANGE = 2*np.pi - np.pi / 8
MINVALUERANGE = 0 + np.pi/8
def get_artificial_data(n_samples=400, n_features=2, centers=2, seed=13):
  X, y = make_blobs(n_samples=n_samples, n_features=n_features, centers=centers, random_state=seed)

  X = preprocessing.MinMaxScaler(feature_range=(MINVALUERANGE, MAXVALUERANGE)).fit_transform(X)
  y = 2*y -1

  return X, y

n_classes = 2
X, y = get_artificial_data(centers=n_classes, seed=112)

print(X[:5])
X = np.array([ list(x) + list(x) for x in X ])
print(X[:5])

circuit, dev, n_params = get_pennylane_circuit_from_file('circuits/CostaSH/4qubits/D.descr', {'&L' : 1})
weights = np.random.randn(n_params, requires_grad=True)
bias = np.array([0.0], requires_grad=True)
circuit_params = {'encoding': 'phase', 'meas' : 'expval', 'measwire': [0]}

print2D_decision_region(circuit, weights, bias, X, y, circuit_params, 2)

# qc = get_unbound_circuit_from_file('circuits/CostaSH/1qubit/ru.descr')
# print(qc)

# n_features = 2
# iqc_gate = get_model_unitary('IQC', n_features)

# params = {p : np.random.random() for p in iqc_gate.params}
# bound_gate = iqc_gate.assign_parameters(params, False)
# unitary_matrix = bound_gate.to_matrix()
# print(unitary_matrix)


# # a o circuito com os parâmetros fornecidos qc,_,_ = circuit_model(data=tx[0],w=tw,counter=counter,qubits=qubits,N_qubits=N_qubits,N_features=NF,model=MODEL,folder=folder,N_qubits_tgt=None,N_layers=None)
# NF=2
# gate =  get_model_unitary('IQC', N_features=NF)

# qc = get_unbound_circuit_from_file('circuits/CustomUnitary/circuitUni.descr', custom_gates={'gate' : gate})
# print(qc)

# qasm_simulator = Aer.get_backend("qasm_simulator")
# kl_pq = get_KL_divergence(qc, n_shots=10000, nparams=5000, backend=qasm_simulator, reuse_circuit_measures=True)

