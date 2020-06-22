import difflib
import re
from math import sqrt


class ErrorModel:

    def __init__(self, bor_tree, file=None):
        self.bor_tree = bor_tree
        self.alpha = 1.5
        self.error_dict = {'replace': {},
                           'insert': {},
                           'delete': {}}
        self.__cor_count = 0

        self.__fit(file)
        self.bor_tree.set_em(self)

    def __fit(self, file):
        with open(file) as f:
            content = f.readlines()
        num_line = 0
        for line in content:
            num_line += 1
            print(f"\r{num_line} lines are processed...", end='', flush=True)
            line = line.lower()
            line = line[:-1]
            index = line.find('\t')
            if index > 0:
                q = line.split('\t')
                if len(re.findall(r"(?u)\w+", q[0])) == len(re.findall(r"(?u)\w+", q[1])):
                    self.fill_dict(q[1], q[0])

    def fill_dict(self, query1, query2):
        inserts = []
        deletes = []
        for i, s in enumerate(difflib.ndiff(query1, query2)):
            if s[0] == ' ':
                continue
            elif s[0] == '-':
                deletes.append((s[-1], i))
            elif s[0] == '+':
                inserts.append((s[-1], i))
            self.__cor_count += 1

        delete_mask = [True] * len(deletes)
        insert_mask = [True] * len(inserts)
        for i in range(len(inserts)):
            for k in range(len(deletes)):
                c1 = deletes[k][0]
                p1 = deletes[k][1]
                for j in range(len(inserts)):
                    c2 = inserts[j][0]
                    p2 = inserts[j][1]
                    if abs(p2 - p1) == 1:
                        delete_mask[k] = False
                        insert_mask[j] = False
                        if c1 not in self.error_dict["replace"]:
                            self.error_dict["replace"][c1] = {}

                        if c2 in self.error_dict["replace"][c1]:
                            self.error_dict["replace"][c1][c2] += 1
                        else:
                            self.error_dict["replace"][c1][c2] = 1

            for k in range(len(deletes)):
                if delete_mask[k]:
                    c = deletes[k][0]
                    if c in self.error_dict["delete"]:
                        self.error_dict["delete"][c] += 1
                    else:
                        self.error_dict["delete"][c] = 1

            for k in range(len(inserts)):
                if insert_mask[k]:
                    c = inserts[k][0]
                    if c in self.error_dict["insert"]:
                        self.error_dict["insert"][c] += 1
                    else:
                        self.error_dict["insert"][c] = 1

    def __weight_func(self, count):
        f = 0.65 ** sqrt(count)
        if f < 0.4:
            return 0.4
        else:
            return f

    def get_weight(self, op_type, c1, c2=None):
        if op_type == "delete" or op_type == "insert":
            if c1 in self.error_dict[op_type]:
                count = self.error_dict[op_type][c1]
            else:
                count = 0
        elif op_type == "replace":
            if c1 in self.error_dict["replace"]:
                if c2 in self.error_dict["replace"][c1]:
                    count = self.error_dict["replace"][c1][c2]
                else:
                    count = 0
            else:
                count = 0
        else:
            count = 0
        return self.__weight_func(count)

    def get_correction(self, word, max_lev):
        correction = self.bor_tree.search(word, max_lev)
        for i in range(len(correction)):
            correction[i][1] = self.alpha ** (-correction[i][1])
        return correction
