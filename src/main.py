import argparse
import yaml

from npfuzz.dependency import make_sequence_set
from npfuzz.mutation import Mutation
from npfuzz.fuzz import Fuzzing
from request.generator import RequestGenerator
from swagger.parser import SwaggerParser
from utils.yaml_utils import *
from utils.common import error, TerminateException
from traceback import print_exc as print_traceback

def read_params(params):
  doc,    errno1 = read_yaml_file(params.target)
  config, errno2 = read_yaml_file(params.config)
  if errno1 == -1 or errno2 == -1:
    error("[*] Program exits...")
  return doc, config

def get_request_set(doc):
  parser = SwaggerParser(doc)
  return parser.get_req_set()

def main(params):
  print('[*] Reading parameters for SwagFuzz...')
  doc, config = read_params(params)
  max_length = get_max_length(config)

  print('[*] Getting request set from swagger...')
  req_set = get_request_set(doc)

  print('[*] Making request sequences set from inferring dependency...')
  seq_set = make_sequence_set(req_set, max_length)

  print('[*] Start Fuzzing')
  f = Fuzzing()
  f.execute(seq_set)

  print ("[*] Finish")


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
  #main(parser.parse_args())
  
  try:
    main(parser.parse_args())
  except TerminateException as e:
    print('\033[1;31m' + str(e.message) + '\033[0;0m')
    exit()
  except Exception as e:
    print("UNHANDLED EXCEPTION OCCUR")
    print(e)
    print_traceback()
    
