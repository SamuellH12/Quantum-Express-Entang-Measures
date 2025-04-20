from qiskit.circuit import Parameter, QuantumCircuit, QuantumRegister, Gate
from qiskit.circuit.library import UnitaryGate
import numpy as np
from scipy.linalg import expm
from scipy.linalg import expm as expMatrix
import math

# Unitaries based on:
# https://github.com/Zuluke/Project_IQC_Expressibility/blob/main/Expressibility%20Measuring%20tgt%20Qubit/qiskit_qc.py

# to handle unitary gates with assign parameters
class ModelUnitaryGate(Gate):
    def __init__(self, model_name, n_qubits, n_data, params, build_matrix):
        super().__init__(name=model_name, num_qubits=n_qubits, params=params)
        self._build_matrix = build_matrix
        self.n_data = n_data
        
    def _define(self):
        q = QuantumRegister(self.num_qubits, 'q')
        qc = QuantumCircuit(q)
        # Initial identity matrix - will be replaced during binding
        qc.append(UnitaryGate(np.eye(2**self.num_qubits)), q)
        self.definition = qc
        
    def assign_parameters(self, parameters, inplace=True):
        param_values = [parameters[p] if isinstance(p, Parameter) else p for p in self.params]
        new_matrix = self._build_matrix(param_values, self.n_data, self.num_qubits)
        new_gate = UnitaryGate(new_matrix)

        if inplace:
            self.definition.data[0] = (new_gate, self.definition.qubits, [])
            return self
        return new_gate

rng=np.random.default_rng(1)
rng2=np.random.default_rng(42)

def get_model_unitary(model: str, N_features):
    """
    """
    N_qubits = math.ceil(np.log2(N_features)+1) #Nqubits do circuito
    n_data = N_features
    n_weights = N_features


    data_params = [Parameter(f'dt{i}') for i in range(n_data)]
    w_params = [Parameter(f'w{i}') for i in range(n_weights)]
    

    if model == 'IQC':

        def build_matrix(params, n_data, n_qubits):
            data = params[:n_data]
            w = params[n_data:]
            w = [[x] for x in w]
            w = np.array(w)

            X_new=np.array(data)
    
            if np.log2(N_features)%2!=0 and np.log2(N_features)!=1:
                for k in range(2**(n_qubits-1) - N_features):
                    w=np.append(w,0)
                    X_new=np.append(X_new,0)
           
            sigmaE=np.diag(X_new)*w.T
            
            #Montando os sigmas
            matriz_pauli_x=np.array([[0,1],[1,0]]) # Matriz de Pauli x
            matriz_pauli_y=np.array([[0,-1j],[1j,0]]) # Matriz de Pauli y
            matriz_pauli_z=np.array([[1,0],[0,-1]]) # Matriz de Pauli z

            sigmaQ=matriz_pauli_x+matriz_pauli_y+matriz_pauli_z

            #Operador Unitário
            U=np.matrix(expMatrix(1j*np.kron(sigmaQ,sigmaE)))
            return U
    
    params = data_params + w_params

    return ModelUnitaryGate(model, N_qubits, n_data, params, build_matrix)