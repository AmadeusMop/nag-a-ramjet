import string
import pymysql
import getpass
from collections import Counter

import time

WORDS_FILE = "sowpods.txt"
WORDS = None
DB_URL = "nagaramjet-db.czaaw1lusahr.us-east-1.rds.amazonaws.com"
DB_PORT = 3306
DB_SCHEMA = "nagaramjet"
SQL_TABLE = "words"
SQL_INSERT = "INSERT INTO {}\nVALUES ('{}',{})".format(SQL_TABLE,"{word}","{}")

ALPHABET = ''.join(map(chr,range(ord('a'),ord('z')+1)))

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
        return any(self.values())

    def _contains_word(self, word):
        if type(word) == Word:
            try:
                return any(self - word.counter)
            except ValueError:
                return (self == word.counter)
        else:
            return bool(self - word) or (self == word)

    def contains_word(self, word):
        if type(word) == Word:
            return self.contains_word(word.counter)
        else:
            return all(self[l] >= word[l] for l in word)

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
        return ''.join(str(self[l]) for l in LetterCounter.LETTERS)

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
#count = 0

def solve(words, letter_pool, root=False):
    if root:
        count = 0
    #global deadends
    if not letter_pool:
        return [[]]
    words = prune(words, letter_pool)
    if not words:
        return False
    else:
        anags = []
        while words:
            word = words[0]
            s = solve(words, letter_pool - word)
            words.pop(0)
            if s:
                anags.extend(map([word].__add__, s))
            if root:
                count += 1
                if not count % ((len(words)//10) + 1):
                    print('.',end='',Flush=True)
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
        
def get_words_from_db(lc, connection):
    if(type(lc) == Word):
        lc = lc.counter
    s = lc.sql_values()
    try:
        print('.',end='')
        with connection.cursor() as cursor:
            sql = "CALL find_words(%s)"
            cursor.execute(sql, (s,))
            print('.',end='')
            result = cursor.fetchall()
            print('.',end='')
        return tuple(map(Word,map((lambda x: x[0]),result)))
    except MySQLError as e:
        connection.close()
        raise e

def connect_to_db():
    c = None
    print("Attempting to connect to database...")
    while c is None:
        try:
            c = pymysql.Connect(
                host=DB_URL, user=input("Username: "),
                database=DB_SCHEMA, password=getpass.getpass())
        except pymysql.MySQLError as e:
            print(e)
            print("Errors encountered. Retrying...")
    print("Successfully connected to database.")
    return c

def main():
    #words = get_words()
    #print(len(words), "words loaded.")
    connection = connect_to_db()
    user_input = input("Enter a word or phrase: ")
    while user_input:
        letters = LetterCounter(user_input)
        print("Querying database", end='')
        words = get_words_from_db(letters,connection)
        print("Query successful. ({} words found)".format(len(words)))
        time.sleep(0.05)
        print("Searching for anagrams", end='', flush=True)
        anags = solve(words, letters, True)
        print(len(anags), "anagrams found.")
        if(input("Display? (y/n): ").lower() != 'n'):
            print_anags(anags)
        user_input = input("Enter a word or phrase: ")

main()
