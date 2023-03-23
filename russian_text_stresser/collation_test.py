import sqlite3
from stressed_cyrillic_tools import unaccentify
import time


def collate_unaccentify(a, b):
    w1 = unaccentify(a)
    w2 = unaccentify(b)
    if w1 < w2:
        return -1
    elif w1 > w2:
        return 1
    else:
        return 0


def test_collation():
    # Connect with the database ruwiktionary.db
    with sqlite3.connect("ruwiktionary.db") as conn:
        cur = conn.cursor()
        # Create the collation
        # conn.create_collation("unaccentify", collate_unaccentify)
        # Create index
        # cur.execute("CREATE INDEX IF NOT EXISTS word_index ON words (word COLLATE unaccentify)")
        t0 = time.time()
        # Get the words with yo
        cur.execute(
            "SELECT word FROM words WHERE word = 'ошибаться' COLLATE unaccentify"
        )
        print(cur.fetchall())
        t1 = time.time()
        print("Time taken: {}".format(t1 - t0))

        cur.close()


if __name__ == "__main__":
    test_collation()
