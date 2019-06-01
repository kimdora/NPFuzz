import argparse
import yaml

from npfuzz.dependency import make_sequence_set
from npfuzz.mutation import Mutation
from npfuzz.fuzz import Fuzzing
from request.generator import RequestGenerator
from swagger.parser import SwaggerParser
from utils.yaml_utils import *
from utils.common import error, TerminateException


def read_params(params):
  doc,    errno1 = read_yaml_file(params.target)
  config, errno2 = read_yaml_file(params.config)
  if errno1 == -1 or errno2 == -1:
    error("[*] Program exits...")
  return doc, config

def get_request_set(doc):
  parser = SwaggerParser(doc)
  return parser.get_req_set()

def find_val(obj, target_key):
  for k, v in obj.items():
    if k == target_key:
      return v
    elif isinstance(v, dict):
      return find_val(v, target_key)
  return None


def main(params):
  print('[*] Reading parameters for SwagFuzz...')
  doc, config = read_params(params)
  max_length = get_max_length(config)

  print('[*] Getting request set from swagger...')
  req_set = get_request_set(doc)

  print('[*] Making request sequences set from inferring dependency...')
  seq_set = make_sequence_set(req_set, max_length)

  '''
  print(seq_set)
  for seq in seq_set:
    for req in (seq):
      print (req.parameter)
      print (req.req_param)
      print (req.path)

  mutation = Mutation(seq_set)
  x = mutation.mutate()
  print(x)
  for seq in x:
    print ('=' * 80)
    for req in (seq):
      print ('-' * 80)
      print (req.method, req.host, req.base_path, req.path)
      print (req.parameter)
      print (req.req_param)
      print (req.path)
  '''
  f = Fuzzing()
  f.execute(seq_set)

  print ("Finish")
  """

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
