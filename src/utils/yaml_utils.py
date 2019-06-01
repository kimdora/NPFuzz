import yaml

from .common import error

# utils for common yaml files
def read_yaml_file(filename):
  try:
    f = open(filename, 'r')
    docs = yaml.safe_load(f)
    f.close()
    return docs, 0
  except:
    error('[Error] Fail to Read {}'.format(filename))
    return _, -1

# utils for only config yaml file
def get_max_length(config, cast=int):
  max_length = config['maxLength']
  return cast(max_length)