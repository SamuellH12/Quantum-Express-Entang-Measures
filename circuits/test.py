# from circuitFromFile import parse_quantum_file 

import pennylane as qml
import numpy as np
from typing import List, Dict, Union

def get_circuit_from_desc(num_qubits: int, classical_bits: int, operators: List[Dict], sequenc_params: List[float]):
    """
    Cria um circuito PennyLane a partir da descrição dos operadores.
    
    Args:
        num_qubits: Número de qubits do circuito
        classical_bits: Número de bits clássicos para medição
        operators: Lista de operadores no formato [{'operator':op, 'qubits':[x,y], 'params':[u,v,w]}, ...]
        sequenc_params: Lista de parâmetros para substituir os '%' no circuito
        
    Returns:
        qml.QNode: Função de circuito PennyLane
        dict: Mapeamento de medições (qubit → bit clássico)
    """
    
    # Configura o dispositivo (pode ser alterado para hardware real)
    dev = qml.device("default.qubit", wires=num_qubits, shots=None)
    
    # Mapeamento de medições
    measurement_map = {}
    classical_wires_used = 0
    
    # Pre-processamento para identificar medições
    for op in operators:
        if op['operator'] == 'MEASSURE':
            for q in op['qubits']:
                if q != -1:  # -1 significa pular esse bit clássico
                    measurement_map[q] = classical_wires_used
                    classical_wires_used += 1
    
    # Verifica se o número de bits clássicos é suficiente
    if classical_wires_used > classical_bits:
        raise ValueError(f"Circuit requires {classical_wires_used} classical bits but only {classical_bits} were provided")
    
    @qml.qnode(dev)
    def quantum_circuit():
        param_idx = 0
        
        for at in operators:
            op = at['operator']
            qubits = at['qubits']
            params = at['params'].copy()  # Fazemos uma cópia para não modificar o original
            
            # Substitui parâmetros não definidos
            for i in range(len(params)):
                if params[i] == '%':
                    if param_idx < len(sequenc_params):
                        params[i] = sequenc_params[param_idx]
                        param_idx += 1
                    else:
                        raise ValueError("Not enough parameters provided to replace all '%' placeholders")
            
            # Aplica as operações
            try:
                if op == 'BAR':
                    qml.Barrier(wires=qubits)
                
                # Portas de um único qubit
                elif op == 'x': qml.PauliX(wires=qubits[0])
                elif op == 'y': qml.PauliY(wires=qubits[0])
                elif op == 'z': qml.PauliZ(wires=qubits[0])
                elif op == 'h': qml.Hadamard(wires=qubits[0])
                elif op == 'rx': qml.RX(params[0], wires=qubits[0])
                elif op == 'ry': qml.RY(params[0], wires=qubits[0])
                elif op == 'rz': qml.RZ(params[0], wires=qubits[0])
                elif op == 'r': 
                    # Porta U geral (theta, phi, lambda)
                    qml.Rot(params[1], params[0], params[2], wires=qubits[0])
                
                # Portas controladas
                elif op == 'cx': qml.CNOT(wires=[qubits[0], qubits[1]])
                elif op == 'cy': qml.CY(wires=[qubits[0], qubits[1]])
                elif op == 'cz': qml.CZ(wires=[qubits[0], qubits[1]])
                elif op == 'ch': qml.CH(wires=[qubits[0], qubits[1]])
                elif op == 'crx': qml.CRX(params[0], wires=[qubits[0], qubits[1]])
                elif op == 'cry': qml.CRY(params[0], wires=[qubits[0], qubits[1]])
                elif op == 'crz': qml.CRZ(params[0], wires=[qubits[0], qubits[1]])
                elif op == 'cr':
                    # Porta U controlada geral (theta, phi, lambda)
                    qml.ControlledPhaseShift(params[2], wires=[qubits[0], qubits[1]])
                    qml.CRY(params[0], wires=[qubits[0], qubits[1]])
                    qml.ControlledPhaseShift(params[1], wires=[qubits[0], qubits[1]])
                
                # Toffoli (CCNOT)
                elif op == 'tfl': qml.Toffoli(wires=[qubits[0], qubits[1], qubits[2]])
                
                # Medição
                elif op == 'MEASSURE':
                    for q in qubits:
                        if q != -1:
                            qml.measure(wires=q)
                
                else:
                    raise ValueError(f"Operator not recognized: {op}")
            
            except Exception as e:
                raise ValueError(f"Error applying operation {at}: {str(e)}")
        
        return [qml.probs(wires=i) for i in range(num_qubits)] if classical_bits == 0 else None
    
    return quantum_circuit, measurement_map

