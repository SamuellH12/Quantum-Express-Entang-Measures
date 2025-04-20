from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit import Parameter, Measure, Gate
from qiskit import transpile
from qiskit_aer import AerSimulator
import numpy as np
from random import random
from math import pi as PI_VALUE
from scipy.special import rel_entr
from qiskit.providers.basic_provider import BasicSimulator
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt


def get_circuit_with_param_conjugate(circuit: QuantumCircuit) -> QuantumCircuit:
    '''
    Creates a conjugated version of a parameterized quantum circuit with:
    - Operation order reversed
    - Parameters renamed with 'conj_' prefix
    - Original measurements preserved at the end

    Used for constructing conjugate circuits in KL divergence calculation.
    '''

    qc = circuit.copy()

    # Pra manter as mesmas medições, mas no final
    measures = []
    for op, qargs, cargs in qc.data:
        if isinstance(op, Measure):
            measures.append((qargs, cargs))
    cr = qc.cregs
    qc.remove_final_measurements()
    
    rev_ops = reversed(qc.data)
    for gate, qargs, cargs in rev_ops:
        new_gate = gate
        if gate.params:
            new_params = [Parameter(f'conj_{param.name}') for param in gate.params]
            new_gate = gate.__class__(*new_params)
        
        qc.append(new_gate, qargs, cargs)
    
    # colocar as medições de volta
    qc.add_register(*cr)
    for qarg, carg in measures:
        qc.measure(qarg, carg)

    return qc


IMAGINARY_UNIT = (-1)**(1/2) # sqrt(-1)

def P_harr(l,u,N):
    return (1-l)**(N-1)-(1-u)**(N-1)

def get_KL_divergence(circuit : QuantumCircuit, n_shots = 10000, nparams=2000, reuse_circuit_measures = False, n_bins=75, backend=None) -> float:
    '''
    Computes the Kullback-Leibler (KL) divergence between the parameterized
    quantum circuit and the Haar-random distribution.\n
    Measures how well the circuit explores the Hilbert space when parameters are randomized.\n
    Lower values indicate closer resemblance to Haar-random behavior.\n\n
    + Parameters:\n
    \t- nparams: Number of random parameter sets to sample
    \t- n_shots: Measurement shots per parameter set
    \t- reuse_circuit_measures: Keep existing measurements if True, else measure all qubits
    \t- n_bins: Histogram bins for probability distribution 
    '''
    if backend is None: backend = BasicSimulator()
    n_qubits = len(circuit.qubits)
    b_list = [ i/n_bins for i in range(n_bins+1) ] # b_cent = [b_list[i] + (1/n_bins) for i in range(n_bins)]
    harr_hist = [ P_harr(b_list[i], b_list[i+1], 2**n_qubits) for i in range(n_bins) ]
    
    # conjugado = get_circuit_with_param_conjugate(circuit)
    conjugado = circuit.copy()
    
    if not reuse_circuit_measures:
        conjugado.remove_final_measurements()
        conjugado.measure_all()

    n_classic = conjugado.num_clbits
    zeros = '0' * n_classic 

    fidelity=[]    
    for _ in range(nparams):
        qc = conjugado.copy()
        param_binding = {p : 2.0*PI_VALUE*random() for p in qc.parameters}
        qc.assign_parameters(param_binding, inplace=True)
        
        for instruction, qargs, cargs in qc.data:
            if hasattr(instruction, 'assign_parameters'):
                instruction.assign_parameters(param_binding, inplace=True)
        
        qc = qc.decompose()
        counts = backend.run(qc, shots=n_shots).result().get_counts()

        ratio = counts.get(zeros, 0) / n_shots
        fidelity.append(ratio)

    weights = np.ones_like(fidelity)/float(len(fidelity))
    P_hist=np.histogram(fidelity, bins=b_list, weights=weights, range=[0, 1])[0]
    kl_pq = rel_entr(P_hist, harr_hist)
    

    plt.hist(fidelity, bins=b_list, weights=weights, range=[0, 1], label='IQC')
    bins_x=[]    
    for i in range(75): bins_x.append(b_list[1]+b_list[i])
    plt.plot(bins_x, harr_hist, label='Harr')
    plt.legend(loc='upper right')
    plt.ylabel('Probability')
    plt.xlabel('Fidelity')
    plt.savefig('fig.png')


    return sum(kl_pq)
