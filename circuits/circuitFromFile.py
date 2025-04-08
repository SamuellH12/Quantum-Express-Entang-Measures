from qiskit import QuantumCircuit

def parse_params_file(path: str):
    '''
    Read the params in the path file and return a
    dict with named params, list of sequencial params\n
    ({}, [])
    '''
    nameds = {}
    sequenc = []
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()

                # ignore comments
                if not line or line.startswith('#'): continue
                
                # named params
                if line.startswith('&'):
                    name, value = line.split()
                    nameds[name] = float(value)
                # sequencial params
                else:
                    sequenc.extend( [float(v) for v in line.split()] )

    except FileNotFoundError:
        print(f"Params file not found {path}")
        return ({}, [])
    except:
        print(f"An error occur while reading the params file {path}")
        return ({}, [])
    
    return (nameds, sequenc)


# Lê o arquivo e retorna uma lista com os operadores 
def parse_quantum_file(path: str, named_params = {}):
    '''
    Read the file and return a tuple with:\n
    \tint: the number of qubits\n
    \tint: the number of classic bits\n
    \tlist: a list of operators and its qubits and params 
    (here params maybe be characters %)\n
    \tint: the number of sequence params\n
    \tlist: a list of sequence params read from the params file (if exists)\n
    (num_qubits, classical_bits, operators, num_of_params, sequenc_params)
    '''
    params_path = None
    num_qubits = 0
    classical_bits = 0
    operators = []
    current_layer = None
    layer_repeat = 0
    sequenc_params = []
    num_of_params = 0
    
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # ignore comments
                if not line or line.startswith('#'): continue
                
                # header / cabeçalho
                if line.startswith('Q '): num_qubits = int(line.split()[1])
                elif line.startswith('PARAM '): 
                    params_path = line.split()[1]
                    nmd_params, seq_params = parse_params_file(params_path)

                    sequenc_params = seq_params
                    #named params by argument override the named params in file
                    for k in nmd_params:
                        if k not in named_params: 
                            named_params[k] = nmd_params[k]

                # Barrier
                elif line.startswith('BAR'):
                    if current_layer != None: current_layer.append({'operator': 'BAR'})
                    else: operators.append({'operator': 'BAR'})
                
                # Meassure
                elif line.startswith('MEASSURE'):
                    opr = {'operator': 'MEASSURE', 'qubits': [], 'params':[]}
                    values = line.split()[1:]
                    for i, v in enumerate(values):
                        if v != '-':
                            opr['qubits'].append(int(v))
                            opr['params'].append(i)
                    
                    if current_layer != None: current_layer.append(opr)
                    else: operators.append(opr)
                    
                    classical_bits = max(classical_bits, len(values))
                
                # Layers
                elif line.startswith('LAYER'):
                    parts = line.split()
                    layer_repeat = parts[1] #it can be a named parameter
                    current_layer = []

                    if layer_repeat.startswith('&'):
                        if layer_repeat in named_params:
                            layer_repeat = named_params[layer_repeat]
                        else: #if the named param dont exist, put the value 0
                            print(f'Named parameter {layer_repeat} not found. Making it 0')
                            layer_repeat = 0
                            
                    layer_repeat = int(layer_repeat)
                
                elif line.startswith('ENDLAYER'):
                    for _ in range(layer_repeat): 
                        operators.extend(current_layer)
                    # operators.append({'operator':'LAYER', 'operatorList':current_layer, 'repeat':layer_repeat})
                    current_layer = None
                
                # others operators
                else:
                    parts = line.split()
                    op = parts[0]
                    qubits = []
                    params = []
                    
                    # single qubit gates
                    if op in ['x', 'y', 'z', 'h', 'rx', 'ry', 'rz', 'ru']:
                        qubits = [int(parts[1])]
                        if len(parts) > 2:
                            params = parts[2:]
                    
                    # controled gates
                    elif op in ['cx', 'cy', 'cz', 'ch', 'crx', 'cry', 'crz', 'cru']:
                        qubits = [int(parts[1]), int(parts[2])]
                        if len(parts) > 3:
                            params = parts[3:]

                        if op == 'cru' and len(params) <= 3: params.append(0)  # global fase if not provided
                    
                    # toffoli gate
                    elif op in ['tfl']:
                        qubits = [int(parts[1]), int(parts[2]), int(parts[2])]
                    
                    else:
                        print(f"Operator not identified: {line}")
                        continue

                    # get the named params and convert to float
                    for i in range(len(params)):
                        if params[i].startswith('&'):
                            if params[i] in named_params: 
                                    params[i] = named_params[params[i]]
                            else:  #if the named param dont exist, make it %
                                print(f'Named parameter {params[i]} not found. Making it a sequence parameter')
                                params[i] = '%'
                        elif params[i] != '%':
                            params[i] = float(params[i])

                    # put it in operator or layers
                    operation = {'operator': op, 'qubits': qubits, 'params': params}
                    if current_layer != None: current_layer.append(operation)
                    else: operators.append(operation)

                    num_of_params += params.count('%') * (layer_repeat if current_layer != None else 1)
            
    except FileNotFoundError:
        print(f"Circuit file not found {path}")
        return (-1, -1, [], -1, [])
    except:
        print(f"An error occur while reading the circuit file {path}")
        return (-1, -1, [], -1, [])


    return (num_qubits, classical_bits, operators, num_of_params, sequenc_params)

def get_circuit_from_desc(num_qubits : int, classical_bits : int, operators : list, sequenc_params : list):
    
    qc = QuantumCircuit(num_qubits, classical_bits)

    param_idx = 0

    for at in operators:
        op = at['operator']

        if op == 'BAR':
            qc.barrier()
            continue
        
        qubits = at['qubits']
        params = at['params']

        for i in range(len(params)):
            if params[i] == '%':
                if param_idx < len(sequenc_params):
                    params[i] = sequenc_params[param_idx] 
                    param_idx += 1
                else:
                    print("!!! The amount of needed parameters is less than the number of circuit parameters !!!")
                    print("!!! Circuit is incomplete !!!")
                    return qc

        try:
            if op == 'MEASSURE':
                for q, c in zip(qubits, params):
                    qc.measure(q, c)
            # single qubits operators
            elif op == 'x': qc.x(*qubits)
            elif op == 'y': qc.y(*qubits)
            elif op == 'y': qc.z(*qubits)
            elif op == 'h': qc.h(*qubits)
            elif op == 'rx': qc.rx(*params, *qubits)
            elif op == 'ry': qc.ry(*params, *qubits)
            elif op == 'rz': qc.rz(*params, *qubits)
            elif op == 'ru': qc.u(*params, *qubits)
            # controled
            elif op == 'cx': qc.cx(*qubits)
            elif op == 'cy': qc.cy(*qubits)
            elif op == 'cz': qc.cz(*qubits)
            elif op == 'ch': qc.ch(*qubits)
            elif op == 'crx': qc.crx(*params, *qubits)
            elif op == 'cry': qc.cry(*params, *qubits)
            elif op == 'crz': qc.crz(*params, *qubits)
            elif op == 'cru': qc.cu(*params, *qubits)
            elif op == 'tfl': qc.ccx(*qubits)
            else:
                print(f"Operator not recognized: {op}")
        except:
            print(f'!!! Some error occurr with {at}. Verify your circuit description !!!')
            print("!!! Circuit is incomplete !!!")
    
    return qc


def get_circuit_from_file(path: str, named_params = {}, sequenc_params = None):
    n_qubits, c_bits, operators, n_params, seq_params = parse_quantum_file(path, named_params)

    # if don't pass the parameters, use the file parameters
    if not sequence_params: sequence_params = seq_params 

    return get_circuit_from_desc(n_qubits, c_bits, operators, sequenc_params)