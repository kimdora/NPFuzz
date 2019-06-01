from sqlite3 import connect as sqlite3_open
from request.generator import RequestGenerator
from request.request import Request
from utils.common import TerminateException 
from .mutation import Mutation

class Fuzzing:
  def __init__(self):
    self.db = sqlite3_open('result.db')
    self.context = None
    self.indepenent_item = None

  def _log(self, seq, result):
    pass

  def _init_context(self):
    self.context = {}
    self.independent_item = []

  def execute(self, seqSet):
    if not isinstance(seqSet, list):
      raise TerminateException('Fuzzing.execute should require list')

    for seq in seqSet:
      self._init_context()
      last_req = seq[-1:][0]

      # build up context
      for req in seq[:-1]:
        self._request(req)

      # do mutate      
      self._request_mutation(last_req)
      print(self.context)

  def _infer_context_parameter(self, req):
    t = Mutation([])
    body = t.remove_param_object(req.parameter)
    path = t.remove_path_object(req.req_param)

    for category in body:
      for item in body[category]:
        if req.method == 'post':
          self.independent_item.append(item)
        else:
          self.context.update({item: [body[category][item], None]})
  
    for item in path:
      self.context.update({item: [path[item], None]})

  def _request(self, req, parameters=None):
    if not isinstance(req, Request):
      raise TerminateException('Fuzzing._request should require Request object')
    self._infer_context_parameter(req)

    gen = RequestGenerator(req)
    for key, val in parameters:
      gen.set_parameter(key, val)
    response_code, content = gen.execute()
    return (response_code, content)

  def _request_mutation(self, req):
    # change type ==> new reqSet(seq) or just change in mutation?
    response_code, content = self._request(req, {})
    return response_code, content, 'how it mutated'

if __name__ == '__main__':
  pass

