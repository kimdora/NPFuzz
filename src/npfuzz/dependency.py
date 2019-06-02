def make_graph(req_set, max_len):
  starts = [req for req in req_set if req.has_dependencies_with([])]
  g = {}
  graph = {}
  consumes = {}
  produces = {}
  d = {}
  for req in req_set:
    consumes[req] = list(req.consume())
    produces[req] = list(req.produce([req]))
  
  for k, v in produces.items():
    for e in v:
      if not e in d:
        d[e] = [k]
      else:
        d[e].append(k)


  for req in req_set:
    for c in consumes[req]:
      for e in d[c]:
        if not req in g:
          g[req] = [e]
        else:
          g[req].append(e)

  # 5 -> [2, 4]
  # 4 -> [2]
  # 3 -> [2]
  
  # 2 -> [3, 4]
  # 4 -> 5

  # 3 -> [2]
  # 4 -> [2]
  # 5 -> [2, 4]

  tmp = g.copy()

  for k, v in g.items():
    if len(v) == 1 and k in tmp:
      if not v[0] in graph:
        graph[v[0]] = [k]
        del tmp[k]
      else:
        graph[v[0]].append(k)
        del tmp[k]

  while check(tmp):
    for k, v in g.items():
      if k in tmp:
        for e in v:
          if not e in graph:
            graph[e] = [k]
            tmp[k].remove(e)
          else:
            tmp[k].remove(e)

  return starts, graph

def check(d):
  for k, v in d.items():
    if len(v) >= 1:
      return True
  return False

def dfs(visited, graph, s, stack, seq_set):
  if not s in graph:
    return seq_set
  visited.append(s)

  for v in graph[s]:
    stack.append(v)
    tmp = list(stack)
    seq_set = seq_set + [tmp]

    if not v in visited and v in graph:
      seq_set = dfs(visited, graph, v, stack, seq_set)
      stack.pop()
    else:
      stack.pop()
  return seq_set

def make_sequence_set(req_set, max_len):
  starts, graph = make_graph(req_set, max_len)

  seq_set = []
  for s in starts:
    seq_set.append([s])
    seq_set = dfs([], graph, s, [s], seq_set)

  return seq_set



