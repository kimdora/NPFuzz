import argparse
import yaml

from swagger.parser import SwaggerParser

def main(params):
  # 1. Parse swaager yaml file and get reqSet
  try:
    swagger_parser = SwaggerParser(params.target)
    reqSet = swagger_parser.get_req_set()
    print(reqSet)
  except FileNotFoundError:
    error('No such file: {}'.format(params.target))
  # 2.
  # 3.

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
  parser.add_argument('--config', required=True, metavar='config.yaml',                                         help='configuration file')
  exit(main(parser.parse_args()))