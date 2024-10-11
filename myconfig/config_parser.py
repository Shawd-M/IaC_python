import yaml

def read_yaml_file(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data