import yaml
config_file=open("config.yaml")
config = yaml.load(config_file, Loader=yaml.FullLoader)