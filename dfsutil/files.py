import pathlib

def get_parent_path(file: str):
    parent_dir = pathlib.Path(file).parent.resolve()
    return parent_dir