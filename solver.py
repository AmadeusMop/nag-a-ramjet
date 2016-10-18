import string,collections

def get_words():
    return ["nag a RAM 123", "Anagram", "nag", "a", "ram", "mAr "]

def get_letters(word):
    word = sanitize(word)
    counter = collections.Counter(word)
    return counter

def sanitize(word):
    word = word.lower()
    word = list(filter(lambda x: x in string.ascii_lowercase, word))
    return word

def main():
    words = get_words()
    letters_dict = dict();

    for word in words:
        letters = get_letters(word)
        letters_dict[word] = ''.join(sorted(letters.elements()))

    print(letters_dict)

main()
