def levenshtein_osa(a: str, b: str) -> int:
    """A slightly-modified version of the traditional Levenshtein string
    distance algorithm that counts an adjacent character swap as one operation.

    For example, traditional Levenshtein would see ab and ba and need to do a
    deletion and then insertion (ab -> a -> ba) whereas this version can
    just swap them in one go.
    """
    a_len = len(a)
    b_len = len(b)
    D = [[0] * (b_len + 1) for i in range(a_len + 1)]

    for i in range(a_len + 1):
        D[i][0] = i
    for j in range(b_len + 1):
        D[0][j] = j

    for i in range(1, a_len + 1):
        for j in range(1, b_len + 1):
            cost = (a[i - 1] != b[j - 1])
            D[i][j] = min(D[i - 1][j] + 1,            # deletion
                          D[i][j - 1] + 1,            # insertion
                          D[i - 1][j - 1] + cost)     # substitution
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] \
                    and a[i - 2] == b[j - 1]:
                D[i][j] = min(
                    D[i][j], D[i - 2][j - 2] + 1      # adjacent transposition
                )

    return D[-1][-1]


def lcs_table(search: str, text: str) -> int:
    """Computes the longest common subsequence table of two strings."""
    search_len = len(search)
    text_len = len(text)
    L = [[0] * (text_len + 1) for _ in range(search_len + 1)]

    for i in range(1, search_len + 1):
        for j in range(1, text_len + 1):
            if search[i - 1] == text[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    return L


def lcs_length(search: str, text: str) -> int:
    """Finds the length of the longest common subsequence between two
    strings.
    """
    L = lcs_table(search, text)

    return L[-1][-1]


if __name__ == '__main__':
    levenshtein_osa(
        'supercalifragiliciousexpialidocious',
        'superdupercalifragiliciousness'
    )
    s = 'test'
    t = 'tes'
    indices = lcs_length(s, t)
    print('done')
