import os

def get_files_of_type(root_dir, extension) -> str:
    file_paths = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
                file_paths[-1] = file_paths[-1].replace('\\', '/')
    
    return file_paths

def get_circuit_path_list(path='.') -> str:
    return get_files_of_type(path, '.descr')