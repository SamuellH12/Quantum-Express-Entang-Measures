from  .circuitFromFile import parse_quantum_file
import pennylane as qml

CIRCUIT_DEFAULT_ARGS = {'weights': [], 
                        'input': None, 
                        'encoding': 'phase', 
                        'meas': 'expval', 
                        'measwire': None,
                        'run_quiet' : False}

def get_pennylane_circuit_from_desc(num_qubits : int, operators : list, dev : qml.device = None) -> tuple[callable, qml.device, int]:
    '''
    Generates a parameterized PennyLane quantum circuit from a gate description list.
    
    Args:
        num_qubits (int): Number of qubits in the circuit
        operators (list): List of gate operations in dictionary format
        dev (qml.Device): Optional PennyLane device (default: 'default.qubit')
    
    Returns:
        tuple: (circuit_function, quantum_device, num_trainable_params)
               - circuit_function: Callable that takes weights, input, and measurement options
               - quantum_device: Associated PennyLane device
               - num_trainable_params: Number of trainable parameters required
    
    '''
    # initial definitions and count of params
    if dev is None: 
        dev = qml.device("default.qubit", wires=num_qubits, shots=None)

    num_of_params = 0
    for at in operators:
        if at['operator'] != 'BAR':
            num_of_params += at['params'].count('%')
    ###


    ### Circuit definition ###
    @qml.qnode(dev)
    def circuit(weights : list = [], input : list = None, encoding : str = 'phase', meas : str ='expval', measwire : list = None, run_quiet=False):
        '''
        Executable quantum circuit with embedded data processing.
        
        Args:
            weights (list): Trainable parameters for parameterized gates
            input (list): Classical input data for encoding
            encoding (str): Data encoding scheme:
                        - 'phase'/'phasex': RX rotations (1 feature per qubit)
                        - 'phasey': RY rotations (1 feature per qubit)
                        - 'amplitude': Amplitude encoding (2^n features)
            meas (str): Measurement type:
                        - 'expval'/'expvalz': Pauli-Z expectation
                        - 'expvalx': Pauli-X expectation
                        - 'expvaly': Pauli-Y expectation
                        - 'probs': Probability distribution
            measwire (list): Qubits to measure (None = use the provided on file/description)
        
        Returns:
            Measurement results based on 'meas' argument
        '''
        param_idx = 0
        measures = []

        # input loading
        encoding = encoding.lower()
        if encoding == 'phasex' or encoding == 'phase':
            if len(input) != num_qubits and run_quiet == False: 
                print(f"!!! Warning !!! {len(input)} input data and {num_qubits} in the circuit" )
            
            for i, theta in enumerate(input):
                qml.RX(theta, i)

        elif encoding == 'phasey':
            if len(input) != num_qubits and run_quiet == False: 
                print(f"!!! Warning !!! {len(input)} input data and {num_qubits} in the circuit" )
            
            for i, theta in enumerate(input):
                qml.RY(theta, i)

        elif encoding == 'amplitude':
            qml.AmplitudeEmbedding(input, wires=range(num_qubits), normalize=True)
        
        else:
            raise ValueError(f"Input Encoding {encoding} not recognized or not suported")
        
        qml.Barrier(wires=range(num_qubits))
        # end input loading #

        # Circuit definition
        for at in operators:
            op = at['operator']

            if op == 'BAR':
                qml.Barrier(wires=range(num_qubits))
                continue
            
            qubits = at['qubits']
            params = at['params'].copy()

            for i in range(len(params)):
                if params[i] == '%':
                    if param_idx < len(weights):
                        params[i] = weights[param_idx] 
                        param_idx += 1
                    else:
                        raise ValueError("!!! The amount of given parameters is less than the number of circuit parameters !!!")
            try: 
                # measure
                if op == 'MEASURE': measures.extend(qubits)
                # single qubits operators
                elif op == 'x': qml.X(qubits)
                elif op == 'y': qml.Y(qubits)
                elif op == 'z': qml.Z(qubits)
                elif op == 'h': qml.H(qubits)
                elif op == 'rx': qml.RX(*params, qubits)
                elif op == 'ry': qml.RY(*params, qubits)
                elif op == 'rz': qml.RZ(*params, qubits)
                elif op == 'ru': qml.Rot(*params,qubits)
                # controled
                elif op == 'cx': qml.CNOT(qubits)
                elif op == 'cy': qml.CY(qubits)
                elif op == 'cz': qml.CZ(qubits)
                elif op == 'ch': qml.CH(qubits)
                elif op == 'crx': qml.CRX(*params, qubits)
                elif op == 'cry': qml.CRY(*params, qubits)
                elif op == 'crz': qml.CRZ(*params, qubits)
                elif op == 'cru': qml.CRot(*params[:3],qubits) # qiskit accepts a 4th param, but pennylane don't
                elif op == 'tfl': qml.Toffoli(qubits)
                else:
                    raise ValueError(f"Operator {op} not recognized or not suported")
                    
            except Exception as e:
                raise ValueError(f"Error applying operation {at}:\n {str(e)}")
        # end Circuit definition for

        # measures
        if measwire is not None: measures = measwire
        if len(measures) == 0: 
            raise ValueError(f"At least one qubit needs to be measured!!!")
        
        meas = meas.lower()

        if   meas == 'expvalx':
            return [qml.expval(qml.PauliX(q)) for q in measures]
        elif meas == 'expvaly':
            return [qml.expval(qml.PauliY(q)) for q in measures]
        elif meas == 'expvalz' or meas == 'expval':
            return [qml.expval(qml.PauliZ(q)) for q in measures]
        elif meas == 'probs':
            return qml.probs(wires=measures)
        else:
            raise ValueError(f"measure {meas} not recognized or not suported")
        
        return None
    ### end circuit function ###
    
    return circuit, dev, num_of_params


def get_pennylane_circuit_from_file(path: str, named_params = {}, dev = None) -> tuple[callable, qml.device, int]:
    '''
    Generates a PennyLane circuit from a quantum circuit description file.
    
    Args:
        path (str): Path to circuit description file
        named_params (dict): Optional predefined parameters for the circuit
        dev (qml.Device): Custom PennyLane device (default: 'default.qubit')
    
    Returns:
        tuple: (circuit_function, quantum_device, num_trainable_params)
               - circuit_function: Callable that takes weights, input, and measurement options
               - quantum_device: Associated PennyLane device
               - num_trainable_params: Number of trainable parameters required
    
    ```def Circuit(weights : list = [], input : list = None, encoding : str = ' phase', meas : str ='expval', measwire : list = None) ```

    '''
    n_qubits, c_bits, operators, n_params, seq_params = parse_quantum_file(path, named_params)

    return get_pennylane_circuit_from_desc(n_qubits, operators, dev)