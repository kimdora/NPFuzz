from sqlite3 import connect as sqlite3_open
from request.generator import RequestGenerator
from request.request import Request
from utils.common import TerminateException 
class Fuzzing:
  def __init__(self):
    self.db = sqlite3_open('result.db')
    self.context = None
    self.indepdent_element = None

  def _log(self, seq, result):
    pass

  def _init_context(self):
    self.context = {}
    self.indepedent_element = []

  def execute(self, seqSet):
    if not isinstance(seqSet, list):
      raise TerminateException('Fuzzing.execute should require list')

    self._init_context()
    for seq in seqSet:
      last_req = seq[-1:][0]

      # build up context
      for req in seq[:-1]:
        self._request(req)

      # do mutate      
      self._request_mutation(last_req)

  def _infer_context_parameter(self, req):
    if req.dependency

  def _request(self, req, parameters=None):
    if not isinstance(req, Request):
      raise TerminateException('Fuzzing._request should require Request object')
    print('-' * 80)
    print(req.method, req.host, req.base_path, req.path)
    print(req.dependency)
    print(req.req_param)
    #print(req.parameter)

    gen = RequestGenerator(req)
    #gen.set_parameter()
    
  def _request_mutation(self, req):
    return self._request(req, {})

if __name__ == '__main__':
  pass

