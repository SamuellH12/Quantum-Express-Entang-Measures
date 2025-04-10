from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit import Parameter, Measure
from qiskit import transpile
from qiskit_aer import AerSimulator
import numpy as np
from random import random
from math import pi as PI_VALUE
from scipy.special import rel_entr
from qiskit.providers.basic_provider import BasicSimulator
import matplotlib.pyplot as plt

def get_circuit_with_param_conjugate(circuit: QuantumCircuit) -> QuantumCircuit:
    
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

def get_KL_divergence(circuit : QuantumCircuit, n_shots=10000, nparams=2000, n_bins=75, backend=None):
    if backend is None: backend = BasicSimulator()
    n_qubits = len(circuit.qubits)
    b_list = [ i/n_bins for i in range(n_bins+1) ]
    # b_cent = [b_list[i] + (1/n_bins) for i in range(n_bins)]
    harr_hist = [ P_harr(b_list[i], b_list[i+1], 2**n_qubits) for i in range(n_bins) ]
    zeros = ''; 
    for _ in range(n_qubits): zeros += '0'
    # print(circuit)
    conjugado = get_circuit_with_param_conjugate(circuit)
    # print(conjugado)

    fidelity=[]    
    for _ in range(nparams):

        qc = conjugado.copy()
        qc.assign_parameters({p : 2.0*PI_VALUE*random() for p in qc.parameters}, inplace=True)
        
        ## precisa do circuito conjugado ?

        qc.remove_final_measurements()
        qc.measure_all()
        ## mudar measure all como opcional

        counts = backend.run(qc, shots=n_shots).result().get_counts()
        # print(counts)

        ratio = counts.get(zeros, 0) / n_shots
        # print(ratio)
        fidelity.append(ratio)


    weights = np.ones_like(fidelity)/float(len(fidelity))
    P_hist=np.histogram(fidelity, bins=b_list, weights=weights, range=[0, 1])[0]
    kl_pq = rel_entr(P_hist, harr_hist)
    
    return sum(kl_pq)

    # plt.hist(fidelity, bins=b_list)
    # plt.savefig('sla.png')
    # print('KL(P || Q): %.3f nats' % sum(kl_pq))
    # print(P_I_hist)
    # print(kl_pq)
