import pandas as pd
import os


def get_csv_path_list(root_dir, extension = '.csv') -> str:
    file_paths = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
                file_paths[-1] = file_paths[-1].replace('\\', '/')
    
    return file_paths

# concatena os dataframes
def save_dataframe(df_novo, arquivo):
    if os.path.exists(arquivo):
        df_existente = pd.read_csv(arquivo)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    
    df_final.to_csv(arquivo, index=False)



FILESPREFIX = 'Ansatz_reduced_training_reports(CostaSH)'
FILEFINAL = 'Ansatz_reduced_training_reports(CostaSH).csv'

pathlist = get_csv_path_list('.')
pathlist = [(path.split('_')[-2], path) for path in pathlist]
pathlist = [(int(order) if '0' <= order[0] <= '9' else -1, path) for order, path in pathlist]

pathlist = sorted(pathlist)

for _, path in pathlist:
    if FILESPREFIX in path:
        print(path)
        df = pd.read_csv(path)
        save_dataframe(pd.DataFrame(df), FILEFINAL)