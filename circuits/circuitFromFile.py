

# Lê os parâmetros do arquivo passado e retorna:
# Read the params in the path file
# ({}, [])
# dict with named params, list of sequencial params
def parse_params_file(path: str):
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
# Read the file and return a tuple with:
# the number of qubits
# the number of classic bits
# a list of operators and it's qubits and params (here params maybe be characters % or named params)
# the tuple with the params read from the params file (if exists)
# Be carefull if 'operator' == 'LAYER', it fields are different
def parse_quantum_file(path: str):
    params_path = None
    num_qubits = None
    classical_bits = 0
    operators = []
    current_layer = None
    layer_repeat = 0
    
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # ignore comments
                if not line or line.startswith('#'): continue
                
                # header / cabeçalho
                if line.startswith('Q '): num_qubits = int(line.split()[1])
                elif line.startswith('PARAM '): params_path = line.split()[1]

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
                
                elif line.startswith('ENDLAYER'):
                    # for _ in range(layer_repeat): # operators.extend(current_layer)
                    operators.append({'operator':'LAYER', 'operatorList':current_layer, 'repeat':layer_repeat})
                    current_layer = None
                
                # others operators
                else:
                    parts = line.split()
                    op = parts[0]
                    qubits = []
                    params = []
                    
                    # unitary gates
                    if op in ['x', 'y', 'z', 'h', 'rx', 'ry', 'rz', 'r']:
                        qubits = [int(parts[1])]
                        if len(parts) > 2:
                            params = [p if p == '%' or p[0] == '&' else float(p) for p in parts[2:]]
                    
                    # controled gates
                    elif op in ['cx', 'cy', 'cz', 'ch', 'crx', 'cry', 'crz', 'cr']:
                        qubits = [int(parts[1]), int(parts[2])]
                        if len(parts) > 3:
                            params = [p if p == '%' or p[0] == '&' else float(p) for p in parts[3:]]
                    
                    # toffoli gate
                    elif op in ['tfl']:
                        qubits = [int(parts[1]), int(parts[2]), int(parts[2])]
                    
                    else:
                        print(f"Operator was not identified {line}")
                        continue

                    # put it in operator or layers
                    operation = {'operator': op, 'qubits': qubits, 'params': params}
                    if current_layer != None: current_layer.append(operation)
                    else: operators.append(operation)
            
    except FileNotFoundError:
        print(f"Circuit file not found {path}")
        return (-1, -1, [], ({}, []))
    except:
        print(f"An error occur while reading the circuit file {path}")
        return (-1, -1, [], ({}, []))

    # if it has a params file, it get the params
    params = ({}, [])
    if params_path: 
        params = parse_params_file(params_path)

    return (num_qubits, classical_bits, operators, params)

