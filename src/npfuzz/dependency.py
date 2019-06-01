def make_graph(req_set):
  starts = [req for req in req_set if req.has_dependencies_with([])]
  graph = {}
  # starts = [[1], [2]]
  # {2: [3, 4], 3: [5]}
  for s in starts:
    for req in req_set:
      if s != req and req.has_dependencies_with([s]):
        if not s in graph:
          graph[s] = [req]
        else:
          graph[s].append(req)

  return starts, graph

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

def make_sequence_set(req_set):
  starts, graph = make_graph(req_set)

  #starts  = [[1], [2]]
  #graph   = {2: [3, 4], 3: [5]}
  seq_set = []
  for s in starts:
    seq_set.append([s])
    seq_set = dfs([], graph, s, [s], seq_set)

  return seq_set



