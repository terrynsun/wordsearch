# Normalize words, i.e. lowercase and strip spaces.
def normalize(word: str):
    word = word.lower()
    word = word.replace(' ', '')
    return word
