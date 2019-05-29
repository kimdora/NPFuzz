import yaml

def get_max_length(config, cast=int):
  max_length = config['maxLength']
  return cast(max_length)