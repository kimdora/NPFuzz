class BFS:
    def __init__(self, req_set):
        self.seq_set = []
        self.req_set = req_set

        # initialize the number of seqSet at each sequence length
        # for removing duplicate
        self.seq_cnt = [0]

    def search(self, n):
        # when n is 1
        if not self.seq_set:
            self.seq_set = [[req] for req in self.req_set
                                            if req.has_dependencies_with([])]
            self.seq_cnt.append(len(self.seq_set))
            return self.seq_set

        new_seq_set = []
        self.seq_cnt.append(self.seq_cnt[n - 1])
        start = self.seq_cnt[n - 2]
        seq_set = self.seq_set[start:]
        for seq in seq_set:
            for req in self.req_set:
                if req.has_dependencies_with(seq):
                    tmp = seq.copy()
                    tmp.append(req)
                    new_seq_set.append(tmp)
                    self.seq_cnt[n] += 1

        for e in new_seq_set:
            self.seq_set.append(e)

        return self.seq_set
