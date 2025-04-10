from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit_aer import AerSimulator
import numpy as np
from random import random
from math import pi as PI_VALUE
from scipy.special import rel_entr
import matplotlib.pyplot as plt

IMAGINARY_UNIT = (-1)**(1/2) # sqrt(-1)

def P_harr(l,u,N):
    return (1-l)**(N-1)-(1-u)**(N-1)

def get_KL_divergence(circuit : QuantumCircuit, n_shots=10000, nparams=2000, n_bins=75, backend=None):
    if backend is None: backend = AerSimulator()
    n_qubits = len(circuit.qubits)
    b_list = [ i/n_bins for i in range(n_bins+1) ]
    # b_cent = [b_list[i] + (1/n_bins) for i in range(n_bins)]
    harr_hist = [ P_harr(b_list[i], b_list[i+1], 2**n_qubits) for i in range(n_bins) ]
    zeros = ''; 
    for _ in range(n_qubits): zeros += '0'

    fidelity=[]    
    for _ in range(nparams):
        # print(_+1, '/', nparams, end='\r')
        qc = circuit.copy()
        
        for p in qc.parameters:
            qc.assign_parameters({p : 2.0*PI_VALUE*random()}, inplace=True)

        qc.measure_all() # se já tiver meassures, ele adiciona só o que precisa ou tudo?

        qc = transpile(qc, backend)
        result = backend.run(qc, shots=n_shots).result()
        counts = result.get_counts(qc)

        ratio=0
        if zeros in counts: ratio=counts[zeros]/n_shots
        fidelity.append(ratio)
    
    weights = np.ones_like(fidelity)/float(len(fidelity))
    P_I_hist=np.histogram(fidelity, bins=b_list, weights=weights, range=[0, 1])[0]
    kl_pq = rel_entr(P_I_hist, harr_hist)
    
    return kl_pq

    # plt.hist(fidelity, bins=b_list)
    # plt.savefig('sla.png')
    # print('KL(P || Q): %.3f nats' % sum(kl_pq))
    # print(P_I_hist)
    # print(kl_pq)
