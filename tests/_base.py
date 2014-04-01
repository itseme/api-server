import yaml


def load_db():
    return yaml.load(open("tests/test_data.yml"))