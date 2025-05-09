import os

def get_files_of_type(root_dir, extension) -> str:
    file_paths = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
                file_paths[-1] = file_paths[-1].replace('\\', '/')
    
    return file_paths

def get_csv_path_list(path='.') -> str:
    return get_files_of_type(path, '.csv')

def get_pkl_path_list(path='.') -> str:
    return get_files_of_type(path, '.pkl')


import pandas as pd
import pickle

def get_dataframes_and_samples(path='.') -> map:
    csv_paths = get_csv_path_list(path)
    pkl_paths = get_pkl_path_list(path)

    csv_paths  = { paths.split('/')[-1].split('.')[0] : paths for paths in csv_paths }
    pkl_paths  = { paths.split('/')[-1].split('.')[0] : paths for paths in pkl_paths }

    DATASETS = {}

    for name in csv_paths:
        df = pd.read_csv(csv_paths[name])
        df.nome = name

        with open(pkl_paths[name], 'rb') as file:
            metrics = pickle.load(file)
        
        DATASETS[name] = {'df': df,  'samples': metrics['samples']}

    return DATASETS

# concatena os dataframes
def save_dataframe(df_novo, arquivo):
    if os.path.exists(arquivo):
        df_existente = pd.read_csv(arquivo)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    
    df_final.to_csv(arquivo, index=False)