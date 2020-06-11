import numpy as np


def levenshtein_distance(str1, str2, result='distance'):
    m, n = len(str1), len(str2)
    d = np.vstack((np.arange(m + 1)[np.newaxis],
                   np.hstack((np.arange(1, n + 1)[:, np.newaxis], np.zeros((n, m))))))
    for i in range(m):
        for j in range(n):
            d[j + 1, i + 1] = np.min([d[j, i + 1] + 1, d[j + 1, i] + 1, d[j, i] + int(str1[i] != str2[j])])
    if result == 'distance':
        return d[n, m]
    if result == 'matrix':
        return d


def split(line):
    split_line = []
    letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  'abcdefghijklmnopqrstuvwxyz'
                  'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ'
                  'абвгдеёжзийклмнопрстуфхцчшщьыъэюя')

    if not line:
        return split_line

    line = line.lower()

    # word consists of letters
    word = ''
    for c in line:
        if c in letters:
            word += c
        else:
            if word:
                split_line.append(word)
                word = ''
    return split_line
