import string

WORDS_FILE = "sowpods.txt"

class LetterCounter(dict):
    """A counter for counting individual letter frequencies in a given word."""

    LETTERS = frozenset(string.ascii_lowercase)

    def __init__(self, word):
        if type(word) == str:
            word = word.lower()
            set(map(self.inc, word))
        elif type(word) == LetterCounter:
            for l in LetterCounter.LETTERS:
                self[l] = word[l]
        else:
            raise TypeError(word)

    def __missing__(self, key):
        if key in LetterCounter.LETTERS:
            return 0
        else:
            raise KeyError(key)
        
    def __repr__(self):
        return ''.join(sorted(self.elements()))

    def __eq__(self, other):
        if type(other) == type(self):
            return all(self[l] == other[l] for l in other)
        elif type(other) == Word:
            return self == other.counter
        else:
            return NotImplemented

    def __ne__(self, other):
        if type(other) == type(self):
            return any(self[l] != other[l] for l in other)
        elif type(other) == Word:
            return self != other.counter
        else:
            return NotImplemented

    def __lt__(self, other):
        if type(other) == type(self):
            return self <= other and self != other
        elif type(other) == Word:
            return self < other.counter
        else:
            return NotImplemented
    
    def __le__(self, other):
        if type(other) == type(self):
            return all(self[l] <= other[l] for l in other)
        elif type(other) == Word:
            return self <= other.counter
        else:
            return NotImplemented

    def __gt__(self, other):
        if type(other) == type(self):
            return self > other and self != other
        elif type(other) == Word:
            return self > other.counter
        else:
            return NotImplemented
    
    def __ge__(self, other):
        if type(other) == type(self):
            return all(self[l] >= other[l] for l in other)
        elif type(other) == Word:
            return self >= other.counter
        else:
            return NotImplemented

    def __add__(self, other):
        clone = self.clone()
        clone += other
        return clone

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        if type(other) == LetterCounter:
            for l in other:
                self[l] += other[l]
            return self
        elif type(other) == str:
            for l in other:
                self[l] += 1
            return self
        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) == LetterCounter:
            clone = self.clone()
            clone -= other
            return clone
        elif type(other) == Word:
            return self - other.counter
        else:
            return NotImplemented

    def __isub__(self, other):
        if type(other) == LetterCounter:
            for l in other:
                self[l] -= other[l]
                if self[l] < 0:
                    raise ValueError("Negative count occurred in __isub__() call. \nOffending parameters: " + str(self) +" (self), " + str(other) + " (other).")
            return self
        elif type(other) == Word:
            self -= other.counter
        elif type(other) == str:
            for l in other:
                self[l] -= 1
                if self[l] < 0:
                    raise ValueError("Negative count occurred in __isub__() call. \nOffending parameters: " + str(self) +" (self), " + str(other) + " (other).")
            return self
        else:
            return NotImplemented

    def __bool__(self):
        return any(self[l] for l in LetterCounter.LETTERS)

    def contains_word(self, word):
        return self >= word

    def clone(self):
        return LetterCounter(self)
    
    def elements(self):
        for key in self:
            for i in range(self[key]):
                yield key

    def inc(self, key):
        try:
            self[key] += 1
        except KeyError:
            pass

    def subtract(self, other):
        for key in other:
            self[key] -= other[key]


class Word:
    """A wrapper for a word containing its LetterCounter, etc."""
    def __init__(self, word):
        if type(word) != str:
            raise TypeError(word)
        self.word = str(word)
        self.counter = LetterCounter(word.lower())
        
    def __repr__(self):
        return self.word

    def __lt__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self.counter < other.counter

    def __le__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self.counter <= other.counter

    def __eq__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self.counter == other.counter

    def __ne__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self.counter != other.counter

def prune(words, letter_pool):
    words = list(filter(letter_pool.contains_word, words))
    #words = [word for word in words if word <= letter_pool]
    return words

def solve(words, letter_pool, root=False):
    ll = ''
    words = prune(words, letter_pool)
    if not letter_pool:
        return [[]]
    elif not words:
        return False
    else:
        #print("words: ", list(words))
        #print("letters: ", letter_pool)
        witer = (w for w in words)
        anags = []
        for word in witer:
            if root:
                fl = str(word)[0]
                if ll != fl:
                    print('.', end='')
                    ll = fl
                
            #print("word: ", word)
            #print("words: ", list(words))
            #print("letters: ", letter_pool)
            s = solve(words, letter_pool - word)
            words = words[1:]
            #print("s: ", s)
            if s:
                #print("s is truthy")
                anags.extend([word]+l for l in s)
                #anags += [[word] + l for l in s]]
                #print("anags: ", anags)
            #else:
                #print("s is falsey")
                #anags += [[word]]
                #print("anags: ", anags)
        return anags
    
def get_words_test():
    return ["nag a RAM 123", "Anagram", "nag", "a", "ram", "mAr ", "gram"]

def test():
    words = get_words_test()
    letters_dict = dict()

    for word in words:
        letters = Word(word)
        letters_dict[word] = letters

    words_list = letters_dict.values()

    print(letters_dict)
    print("T", letters_dict["Anagram"] == letters_dict["nag a RAM 123"])
    print("T", letters_dict["Anagram"] <= letters_dict["nag a RAM 123"])
    print("F", letters_dict["Anagram"] < letters_dict["nag a RAM 123"])
    print("T", letters_dict["nag"] <= letters_dict["nag a RAM 123"])
    print("T", letters_dict["nag"] < letters_dict["nag a RAM 123"])
    print("F", letters_dict["Anagram"] <= letters_dict["nag"])

    print(list(prune(words_list, LetterCounter("ram nag"))))

    lc = LetterCounter("anagram anagram")
    lcaa = LetterCounter("aaaaaaaa")

    s = solve(words_list, lc)
    if input("Continue? "):
        print('\n'.join([' '.join(str(w) for w in q) for q in s]), sep='\n')
        print("Anagram count: ", len(s))

def print_anags(anags):
    print('\n'.join([' '.join(str(w) for w in l) for l in anags]), sep='\n')


def get_words():
    try:
        file = open(WORDS_FILE)
        words = [Word(word.strip()) for word in file if word.strip()]
        return words
    except IOError as e:
        raise IOError from e

def main():
    words = get_words()
    print(len(words), "words loaded.")
    user_input = input("Enter a word or phrase: ")
    while user_input:
        letters = LetterCounter(user_input)
        anags = solve(words, letters, True)
        print(len(anags), "anagrams found.")
        if(input("Display? (y/n):").lower() != 'n'):
            print_anags(anags)
        user_input = input("Enter a word or phrase: ")

main()
