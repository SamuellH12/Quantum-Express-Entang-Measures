import os
import pandas as pd
from local.listDatabases import get_csv_path_list, get_pkl_path_list, get_dataframes_and_samples
import pickle
from qmlHelper.utils import normalize_X_data

def get_datasets():
    print('getting datasets...')

    DATASET_BY_FEATURES = {}
    DATASETS = get_dataframes_and_samples('./local')

    for name, data in DATASETS.items():

        df = data['df']
        y = df['target']
        X = pd.DataFrame(normalize_X_data(df.drop(columns=['target'])))

        df = pd.concat([X, y], axis=1)
        data['df'] = df
    
    NEW_DATASET = {}

    for dt_name in DATASETS:
        if 'high_noise' not in dt_name:
            NEW_DATASET[dt_name] = DATASETS[dt_name]

    DATASETS = NEW_DATASET

    # ---------------------------------------------- # 
    # ---------------------------------------------- # 
    # ---------------------------------------------- # 

    # organizar o dataset pela quantidade de features e classes
    DATASET_BY_FEATURES = {}

    for name, data in DATASETS.items():

        num_features = len(data['df'].columns) - 1
        num_classes = len(set(data['df']['target']))
        
        if num_features not in DATASET_BY_FEATURES: DATASET_BY_FEATURES[num_features] = {}
        if num_classes not in DATASET_BY_FEATURES[num_features]: DATASET_BY_FEATURES[num_features][num_classes] = {}
        
        DATASET_BY_FEATURES[num_features][num_classes][name] = data

    return DATASET_BY_FEATURES
    # [print([(feat, classes) for classes in DATASET_BY_FEATURES[feat].keys() ]) for feat in DATASET_BY_FEATURES.keys() ]
    # list(DATASET_BY_FEATURES[2][2].keys())


# ---------------------------------------------- # 
# ---------------------------------------------- # 
# ---------------------------------------------- # 

print('getting circuits...')

from circuits.listCircuits import get_circuit_path_list
from circuits.pennylaneCircuitParse import get_pennylane_circuit_from_file

# Circuit list by number of qubits

def get_circuits():
    PATH = 'circuits/CostaSH'
    CIRCUITS = [[]]
    
    CIRCUITS.append([])
    for path in get_circuit_path_list(PATH + '/1qubit'):
        name = path.split('/')[-1].split('.')[0]
        circuit, dev, nparams = get_pennylane_circuit_from_file(path)
        CIRCUITS[1].append( {'name':name, 'circuit' : circuit, 'dev' : dev, 'nparams' : nparams, 'path':path} )

    for i in range(2, 5):
        CIRCUITS.append([])
        for path in get_circuit_path_list(PATH + f'/{i}qubits'):
            name = path.split('/')[-1].split('.')[0]
            circuit, dev, nparams = get_pennylane_circuit_from_file(path, {'&L' : 1})
            CIRCUITS[i].append( {'name':name, 'circuit' : circuit, 'dev' : dev, 'nparams' : nparams, 'path':path} )

    return CIRCUITS
# [print(len(Nqubits), [circuit['name'] for circuit in Nqubits]) for  Nqubits in CIRCUITS ]
# print()


# ---------------------------------------------- # 
# ---------------------------------------------- # 
# ---------------------------------------------- # 


from pennylane.optimize import NesterovMomentumOptimizer, GradientDescentOptimizer, SPSAOptimizer
from qmlHelper.metrics import square_loss_silhouette, square_loss_calinski_harabasz_score, square_loss_davies_bouldin_score

EMBEDDING = ['phasex', 
            #  'phasey', 
             'amplitude']
### (optimizer, opt_params)
OPTIMIZERS = {
              'SPSAOptimizer(10)' : (SPSAOptimizer, [10]),
              # 'GradientDescentOptimizer(1)' : (GradientDescentOptimizer, [1]), 
            #   'NesterovMomentumOptimizer(0.1)' :(NesterovMomentumOptimizer, [0.1]),  
              } 
METRICS = {'silhouette' : square_loss_silhouette, 
           'calinski harabasz' : square_loss_calinski_harabasz_score,
          #  'davies bouldin' : square_loss_davies_bouldin_score
           }


# ---------------------------------------------- # 
# ---------------------------------------------- #  
# ---------------------------------------------- # 

import traceback
from qmlHelper.utils import train_ansatz, cost
from qmlHelper.metrics import unsupervised_accuracy
from sklearn.model_selection import train_test_split

SEED = 157
BATCH_SIZE = 20
STEPS = 80
CIRCUIT_ARGS = {'encoding': 'phase',
                'meas': 'expval',
                'measwire': [0],
                'run_quiet': True}


def run_one_task(use_bias, qubits, circuit_path, circuit_name, nparams, n_feat, n_classes, 
                  df_name, sample_index, dataset,
                  encoding, opt_name, optimizer, opt_params, 
                  metrc_name, metric, wires_to_measure, measure_type ):
    
    circuit, dev, nparams = get_pennylane_circuit_from_file(circuit_path, {'&L' : 1})

    circuit_args = CIRCUIT_ARGS
    circuit_args['encoding'] = encoding
    circuit_args['meas'] = measure_type
    circuit_args['measwire'] = range(wires_to_measure)

    data = dataset.drop(columns=['target'], inplace=False).to_numpy()
    labels = dataset['target'].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split( data, labels, test_size=0.3, random_state=SEED, stratify=labels )
    
    try:
        weights, bias = train_ansatz(circuit  = circuit,
                                    n_params = nparams, 
                                    circuit_args = circuit_args, 
                                    data = X_train, 
                                    labels = y_train, 
                                    batch_size = BATCH_SIZE, 
                                    Steps = STEPS, 
                                    cost_metric = metric, 
                                    opt = optimizer(*opt_params),
                                    seed=SEED, 
                                    threshold_n_classes = n_classes, 
                                    use_bias = use_bias
                                    )   
                                                
        entry = {'ARQUITETURA_ANSATZ' :  circuit_name,
                'INPUT_EMBEDDING': encoding,
                'DATASET': df_name,
                'DATASET_DIVISION_INDEX': sample_index,
                'OPTIMIZER': opt_name,
                'UNSUPERVISED_METRIC': metrc_name,
                'MEASURED_WIRES': wires_to_measure,
                'MEASURE_TYPE': measure_type,
                'TRAIN_METRIC_COST': cost(circuit, weights, bias, metric, X_train, y_train, n_classes, circuit_args),
                'TEST_METRIC_COST':  cost(circuit, weights, bias, metric, X_test,  y_test,  n_classes, circuit_args),
                'TRAIN_ACCURACY': unsupervised_accuracy(circuit, weights, bias, X_train, y_train, n_classes, circuit_args),
                'TEST_ACCURACY': unsupervised_accuracy(circuit, weights, bias, X_test, y_test, n_classes, circuit_args),
                'WEIGHT': weights,
                'BIAS': bias,
                'USE_BIAS': 'YES' if use_bias else 'NO',
        }

        return entry

    except Exception as e:
        entry_id = {'ARQUITETURA_ANSATZ' :  circuit_name, 'INPUT_EMBEDDING': encoding, 'DATASET': df_name, 'DATASET_DIVISION_INDEX': sample_index, 'OPTIMIZER': opt_name, 'UNSUPERVISED_METRIC': metrc_name, 'MEASURED_WIRES': wires_to_measure, 'MEASURE_TYPE': measure_type}
        print('Error at:', entry_id)
        print(f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}")
        return entry_id

def run_one_task_args(args):
    try:
        return run_one_task(*args)
    except Exception as e:
        print("ERROR")
        return {}


# ---------------------------------------------- # 
# ---------------------------------------------- #  
# ---------------------------------------------- # 


def get_tasks(CIRCUITS, DATASET_BY_FEATURES):
    print('getting tasks...')
    TASKS = []
    MAX_SAMPLES = 5

    for use_bias in [True]:
        for qubits in range(1, 5):
            for circuit in CIRCUITS[qubits]:

                for n_feat, datasets_by_class in DATASET_BY_FEATURES.items():
                    for n_classes, datasets_by_name in datasets_by_class.items():
                        for df_name, dataset in datasets_by_name.items():
                            for encoding in EMBEDDING:
                                if encoding == 'amplitude' and n_feat != 2**qubits: continue # 2^N features to N qubits
                                if encoding.startswith('phase') and n_feat > qubits: continue # não há qubits suficientes para carregar os dados                
                                for sample_index, sample in zip(range(MAX_SAMPLES), dataset['samples']):    
                                    for opt_name, (optimizer, opt_params) in OPTIMIZERS.items():
                                        for metrc_name, metric in METRICS.items():
                                            # ENTRY_GROUP = []
                                            # print({'ARQUITETURA_ANSATZ' :  circuit['name'], 'INPUT_EMBEDDING': encoding, 'DATASET': df_name})
                                            for wires_to_measure in [1]: #, n_classes]:
                                                for measure_type in ['expval']: # + 'probs' ?
                                                    if wires_to_measure > qubits: continue
                                                    
                                                    TASKS.append((use_bias, qubits, circuit['path'], circuit['name'], circuit['nparams'], n_feat, n_classes, 
                                                                df_name, sample_index, dataset['df'].loc[sample], 
                                                                encoding, opt_name, optimizer, opt_params, 
                                                                metrc_name, metric, wires_to_measure, measure_type ))

                                                    # ENTRY_GROUP.append(run_one_task(*TASKS[-1]))
                                            ### END OF for wires to measure
                                            # save_dataframe(pd.DataFrame(ENTRY_GROUP), FILENAME)
                                    ### END OF for optimizer
                                ## END OF for samples

    print(f"TASKS: {len(TASKS)}")
    return TASKS

# ---------------------------------------------- # 
# ---------------------------------------------- #  
# ---------------------------------------------- # 

from local.listDatabases import save_dataframe
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm
import os
MAX_WORKERS = max(os.cpu_count() - 1, 1)

# FILENAME = 'reports_data/Ansatz_reduced_training_reports(CostaSH).csv'

def run_task_parallel(tasks, filename, tqdmname):

        results = []
        for task in tqdm(tasks, desc=tqdmname):
            results.append(run_one_task_args(task))

        final_df = pd.DataFrame(results)
        save_dataframe(final_df, filename)
        print(f"Saved {len(results)} results to {filename}")

        return results
        # with tqdm(total=len(tasks)) as pbar:
        #     with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        #         futures = []
        #         for task in tasks: futures.append(executor.submit(run_one_task_args, task))
        #         for future in concurrent.futures.as_completed(futures):
        #             results.append(future.result())
        #             pbar.update(1)

from multiprocessing import freeze_support
import sys
import os
import subprocess
from math import ceil

def main():
    if len(sys.argv) == 1:  # Main process
        SIZE = len(TASKS)
        DIV = int(input('How many divisions do you want? → '))
        
        # Calculate chunk sizes with load balancing
        chunk_size = ceil(SIZE / DIV)
        processes = []
        
        for i in range(DIV):
            start = i * chunk_size
            end = min(start + chunk_size, SIZE)
            if start >= SIZE:
                break
            
            # Spawn subprocess with proper Python executable
            cmd = [
                sys.executable,  # Use same Python interpreter
                os.path.basename(__file__),
                str(start),
                str(end)
            ]
            
            # Start process and keep reference
            proc = subprocess.Popen(cmd)
            processes.append(proc)
            print(f"Started process {proc.pid} for tasks [{start}-{end})")

        # Wait for all processes to complete
        for proc in processes:
            proc.wait()

    elif len(sys.argv) == 3:  # Child process
        try:
            L = int(sys.argv[1])
            R = int(sys.argv[2])
            FILENAME = f'reports_data/Ansatz_reduced_training_reports(CostaSH)_{L}_{R}.csv'
            
            print(f"Processing tasks {L}-{R}")
            run_task_parallel(TASKS[L:R], FILENAME, f'tasks [{L}-{R})')

        except Exception as e:
            print(f"Child process failed: {str(e)}")
            sys.exit(1)

    else:
        print("Invalid arguments:", sys.argv)

if __name__ == '__main__':
    # Initialize shared resources first
    CIRCUITS = get_circuits()
    DATASET_BY_FEATURES = get_datasets()
    TASKS = get_tasks(CIRCUITS, DATASET_BY_FEATURES)
    
    # Windows-specific setup
    if os.name == 'nt':
        from multiprocessing import freeze_support
        freeze_support()
    
    main()