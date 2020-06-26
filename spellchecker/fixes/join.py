class JoinGenerator:

    def __init__(self):
        pass

    def generate_joins(self, words):
        if len(words) < 2:
            return words

        joins = []
        for i in range(len(words) - 1):
            join = words[0:i]
            join.append(words[i] + words[i + 1])
            join.extend(words[i + 2:])
            joins.append(join)

        return joins
