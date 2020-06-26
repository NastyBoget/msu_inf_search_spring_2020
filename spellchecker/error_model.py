import difflib
import re
from math import sqrt


class ErrorModel:

    def __init__(self, bor_tree, file=None):
        self.bor_tree = bor_tree
        # the parameter for computing P(orig|fix)
        self.alpha = 1.5
        self.WORDS = re.compile(r"(?u)\w+")
        # {"replace" : {"char1" : {"char2" : count}}, "insert" : {"char" : count}, "delete" : {"char" : count}}
        self.error_dict = {'replace': {},
                           'insert': {},
                           'delete': {}}
        self.fit(file)
        self.bor_tree.em = self

    def fit(self, file):
        with open(file) as f:
            lines = f.readlines()
        num_line = 0
        for line in lines:
            num_line += 1
            print(f"\r{num_line} lines are processed...", end='', flush=True)
            line = line.lower()
            line = line[:-1]
            index = line.find('\t')
            if index > 0:
                q = line.split('\t')
                # if there is no join or split
                if len(self.WORDS.findall(q[0])) == len(self.WORDS.findall(q[1])):
                    self.fill_dict(q[1], q[0])
        print()

    def fill_dict(self, query1, query2):
        inserts = []
        deletes = []
        for i, item in enumerate(difflib.ndiff(query1, query2)):
            op, letter = item[0], item[1]
            # there is no some correction
            if op == ' ':
                continue
            # there is deletion
            elif op == '-':
                deletes.append((letter, i))
            # there is insertion
            elif op == '+':
                inserts.append((letter, i))

        delete_mask = [True] * len(deletes)
        insert_mask = [True] * len(inserts)
        for i in range(len(inserts)):
            for k in range(len(deletes)):
                # the letter
                char1 = deletes[k][0]
                # the position
                pos1 = deletes[k][1]
                for j in range(len(inserts)):
                    char2 = inserts[j][0]
                    pos2 = inserts[j][1]
                    # there is replacing
                    if abs(pos2 - pos1) == 1:
                        delete_mask[k] = False
                        insert_mask[j] = False
                        if char1 not in self.error_dict["replace"]:
                            self.error_dict["replace"][char1] = {}

                        if char2 in self.error_dict["replace"][char1]:
                            self.error_dict["replace"][char1][char2] += 1
                        else:
                            self.error_dict["replace"][char1][char2] = 1
            # there is deletion
            for k in range(len(deletes)):
                if delete_mask[k]:
                    char = deletes[k][0]
                    if char in self.error_dict["delete"]:
                        self.error_dict["delete"][char] += 1
                    else:
                        self.error_dict["delete"][char] = 1

            # there is insertion
            for k in range(len(inserts)):
                if insert_mask[k]:
                    char = inserts[k][0]
                    if char in self.error_dict["insert"]:
                        self.error_dict["insert"][char] += 1
                    else:
                        self.error_dict["insert"][char] = 1

    @staticmethod
    def weight_func(cnt):
        f = 0.65 ** sqrt(cnt)
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
        return ErrorModel.weight_func(count)

    # P(orig|fix) = alpha ** (-(lev(orig, fix)))
    def get_correction(self, word, max_lev):
        correction = self.bor_tree.search(word, max_lev)
        for i in range(len(correction)):
            correction[i][1] = self.alpha ** (-correction[i][1])
        return correction
