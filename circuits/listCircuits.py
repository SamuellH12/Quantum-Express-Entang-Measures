import os

def get_files_of_type(root_dir, extension):
    file_paths = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
    
    return file_paths

def get_circuit_path_list(path='.'):
    return get_files_of_type(path, '.descr')