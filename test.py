from circuits.pennylaneCircuitParse import get_pennylane_circuit_from_file
from circuits.listCircuits import get_circuit_path_list

print('circuit,num_params')
for path in get_circuit_path_list('circuits/CostaSH'):
  circuit, dev, n_params = get_pennylane_circuit_from_file(path, {'&L' : 1})
  print(path.split('/')[-1].split('.')[0], n_params)