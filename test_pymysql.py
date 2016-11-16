from collections import Counter
import pymysql
import getpass

alphabet = ''.join(map(chr,range(ord('a'),ord('z')+1)))

def to_freqs(s):
    c = Counter(s)
    return ''.join(map(str,map(c.__getitem__,alphabet)))

def get_anags(s):
    connection = pymysql.Connect(
        host="nagaramjet-db.czaaw1lusahr.us-east-1.rds.amazonaws.com",
        user="cillian", database="nagaramjet",
        password=getpass.getpass())
    with connection.cursor() as cursor:
        sql = "CALL find_words(%s)"
        cursor.execute(sql, (to_freqs(s),))
        result = cursor.fetchall()
    connection.close()
    return result

s = input("Word(s) to anagramize: ").lower()
r = get_anags(s)
words = list(map((lambda x: x[0]),r))
print(words)
