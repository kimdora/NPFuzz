import argparse
import yaml

from npfuzz.dependency import make_sequence_set
from restler import *
from request.mutation import Mutation
from request.generator import RequestGenerator
from swagger.parser import SwaggerParser
from utils.config_utils import *
from utils.yaml_utils import read_yaml_file
from utils.common import error, TerminateException

def get_req_set(doc):
  parser = SwaggerParser(doc)
  return parser.get_req_set()

def read_params(params):
  doc,    errno1 = read_yaml_file(params.target)
  config, errno2 = read_yaml_file(params.config)
  if errno1 == -1 or errno2 == -1:
    error("[*] Program exits...")
  return doc, config

def find_val(obj, target_key):
  for k, v in obj.items():
    if k == target_key:
      return v
    elif isinstance(v, dict):
      return find_val(v, target_key)
  return None


def main(params):
  doc, config = read_params(params)
  max_length = get_max_length(config)
  req_set = get_req_set(doc)
  seq_set = make_sequence_set(req_set)
  #print(seq_set)


  """
  # REST-ler method
  n = 1
  bfs = BFS(req_set)
  #bfsfast = BFSFast(req_set)
  #randomwalk = RandomWalk(req_set)

  while n <= max_length:
    seq_set = bfs.search(n)
    print(seq_set)
    #seq_set = render(seq_set, seq_set)
    n = n + 1

  for req in reqs:
    gen = RequestGenerator(req)
    gen.set_parameter('id', 3)
    gen.set_parameter('body', 'Hello World!')
    gen.set_parameter('checksum', '7bf7122c277c5c519267')
    ret = gen.execute()
    print (ret)

  seq_set = [
    [reqs[1], reqs[2]],
    [reqs[1], reqs[3]],
    [reqs[1], reqs[4]]
  ]
  mutation = Mutation(seq_set)
  mutation.mutate()
  print ("Finish")

  from json import loads as json_decode
  context = {'id': None, 'checksum': None}
  for req in seqSet:
    g = RequestGenerator(req[0])
    for key, val in req[1]:
      if val == None:
        val = context[key]
      g.set_parameter(key, val)
    code, body = g.execute()
    print(code, body)
    body_obj = json_decode(body)

    for key in context:
      x = find_val(body_obj, key)
      if x != None:
        context[key] = x




"""
  return



if __name__ == '__main__':
  """ Welcome to "NP Fuzz" which is a REST API Fuzzing with State Diversity.

      This program must need
        1) *.yaml which is a swagger yaml file of target
        2) config.yaml

      For example:
        $ python main.py --target swagger.yaml --config config.yaml

      If you want to know how to use this program, command:
        $ python main.py --help
  """
  parser = argparse.ArgumentParser(
                            description='REST API Fuzzing with State Diversity')
  parser.add_argument('--target', required=True, metavar='*.yaml',
                                  help='swagger yaml file of target')
  parser.add_argument('--config', required=True, metavar='config.yaml',
                                  help='configuration file')
  main(parser.parse_args())
  '''
  try:
  except TerminateException as e:
    print('\033[1;31m' + str(e.message) + '\033[0;0m')
    exit()
  except Exception as e:
    print("UNHANDLED EXCEPTION OCCUR")
    print(e)
  '''
