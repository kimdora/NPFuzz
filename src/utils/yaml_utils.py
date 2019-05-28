import yaml

def read_yaml_file(filename):
  try:
    f = open(filename, 'r')
    docs = yaml.safe_load(f)
    f.close()
    return docs, 0
  except:
    error('[Error] Fail to Read {}'.format(filename))
    return _, -1