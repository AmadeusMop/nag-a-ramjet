import string
from collections import Counter

WORDS_FILE = "sowpods.txt"
WORDS = None
SQL_TABLE = "Words"
SQL_INSERT = "INSERT INTO {}\nVALUES ('{}',{})".format(SQL_TABLE,"{word}","{}")

class LetterCounter(Counter):
    """A counter for counting individual letter frequencies in a given word."""

    LETTERS = tuple(string.ascii_lowercase)

    def __init__(self, word):
        if type(word) == str:
            word = filter(str.isalpha, word.lower())
            super().__init__(word)
        elif type(word) == LetterCounter:
            super().__init__(word)
        elif type(word) == Counter:
            super().__init__(word)
        else:
            raise TypeError(word)

    def __missing__(self, key):
        if key in LetterCounter.LETTERS:
            return 0
        else:
            raise KeyError(key)
        
    def __str__(self):
        return ''.join(sorted(self.elements()))

    def __eq__(self, other):
        if type(other) == LetterCounter:
            return self.items() == other.items()
        elif type(other) == Word:
            return self == other.counter
        else:
            return NotImplemented
    
    def __le__(self, other):
        if type(other) == LetterCounter:
            return all(self[l] <= other[l] for l in other)
        elif type(other) == Word:
            return self <= other.counter
        else:
            return NotImplemented
    
    def __ge__(self, other):
        if type(other) == LetterCounter:
            return all(self[l] >= other[l] for l in other)
        elif type(other) == Word:
            return self >= other.counter
        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) == LetterCounter:
            clone = self.clone()
            clone -= other
            #clone.subtract(other)
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
        return any(self)

    def contains_word(self, word):
        if type(word) == Word:
            try:
                return any(self - word.counter)
            except ValueError:
                return (self == word.counter)
        else:
            return bool(self - word) or (self == word)

    def clone(self):
        return LetterCounter(self)
    
    #def elements(self):
    #    for key in self:
    #        for i in range(self[key]):
    #            yield key

    def inc(self, key):
        try:
            self[key] += 1
        except KeyError:
            pass

    def sql_values(self):
        return (self[l] for l in LetterCounter.LETTERS)

    #def subtract(self, other):
    #    for key in other:
    #        self[key] -= other[key]


class Word:
    """A wrapper for a word containing its LetterCounter, etc."""
    def __init__(self, word):
        if type(word) != str:
            raise TypeError(word)
        self.word = word
        self.hashed = hash(self.word)
        self.counter = LetterCounter(self.word)
        
    def __repr__(self):
        return self.word

    def __len__(self):
        return len(self.word)

    def __hash__(self):
        return self.hashed

    def getfreq(self, key):
        return self.counter(key)

    def sqlize(self):
        return SQL_INSERT.format(','.join(map(str,self.counter.sql_values())), word=self.word)

def prune(words, letter_pool):
    words = list(filter(letter_pool.contains_word, words))
    return words

deadends = []

def solve(words, letter_pool, root=False):
    global deadends
    ll = ''
    if not letter_pool:
        return [[]]
    words = prune(words, letter_pool)
    if not words:
        deadends.append(letter_pool)
        return False
    else:
        #print("words: ", list(words))
        #print("letters: ", letter_pool)
        #witer = iter(words)
        anags = []
        while words:
            word = words[0]
            if root:
                fl = str(word)[0]
                if ll != fl:
                    print('.', end='')
                    ll = fl
                
            #print("word: ", word)
            #print("words: ", list(words))
            #print("letters: ", letter_pool)
            s = solve(words, letter_pool - word)
            words.pop(0)
            #print("s: ", s)
            if s:
                #print("s is truthy")
                anags.extend(map([word].__add__, s))
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
    anags = sorted(anags, key=len)
    for anag in anags:
        print(' '.join(map(str,anag)))
    #print('\n'.join([' '.join(map(str,l)) for l in anags]), sep='\n')


def get_words():
    global WORDS
    if WORDS is not None:
        return WORDS
    else:
        try:
            file = open(WORDS_FILE)
            WORDS = tuple(map(Word, filter(len, map(str.strip, file))))
            return WORDS
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
