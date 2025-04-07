from circuitFromFile import parse_quantum_file 

_, _, op, np, param = parse_quantum_file('circuit0.descr')

for x in op:
    print(x)

print(np)