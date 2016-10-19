import string

class LetterCounter(dict):
    """A counter for counting individual letter frequencies in a given word."""

    LETTERS = frozenset(string.ascii_lowercase)

    def __init__(self, word):
        if type(word) == str:
            word = word.lower()
            for letter in word:
                try:
                    self[letter] += 1
                except KeyError:
                    pass
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
        return all(self[l] == other[l] for l in LetterCounter.LETTERS)

    def __ne__(self, other):
        return any(self[l] != other[l] for l in LetterCounter.LETTERS)

    def __lt__(self, other):
        return self <= other and self != other
    
    def __le__(self, other):
        return all(self[l] <= other[l] for l in LetterCounter.LETTERS)

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
        clone = self.clone()
        clone -= other
        return clone

    def __isub__(self, other):
        if type(other) == LetterCounter:
            for l in other:
                self[l] -= other[l]
            return self
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

    def clone(self):
        return LetterCounter(self)
    
    def elements(self):
        for key in self:
            for i in range(self[key]):
                yield key

    def subtract(self, other):
        for key in other:
            self[key] -= other[key]


def get_words():
    return ["nag a RAM 123", "Anagram", "nag", "a", "ram", "mAr "]

def get_letters(word):
    counter = LetterCounter(word)
    return counter

def main():
    words = get_words()
    letters_dict = dict();

    for word in words:
        letters = get_letters(word)
        letters_dict[word] = letters

    print(letters_dict)
    print(letters_dict["Anagram"] == letters_dict["nag a RAM 123"])
    print(letters_dict["Anagram"] <= letters_dict["nag a RAM 123"])
    print(letters_dict["Anagram"] < letters_dict["nag a RAM 123"])
    print(letters_dict["nag"] <= letters_dict["nag a RAM 123"])
    print(letters_dict["nag"] < letters_dict["nag a RAM 123"])
    print(letters_dict["Anagram"] <= letters_dict["nag"])

main()
