# Russian word stresser for ebooks in epub format

The aim of this program is to stress entire Russian ebooks and to add the dots over the ё. If your ebook is not in the epub format, I would recommend to use Calibre to convert it beforehand.

Right now the program stresses most words, although sometimes the stress is omitted because a) there are multiple options the word could be stressed depending on the context (in the case of замок or все vs всё) or b) simply because they don't appear in my current data source (English Wiktionary). The latter is the case for some short forms of adjectives, I'll try to find a solution to that.

### Installation

First you should download the Github repository and the dictionary database: https://mega.nz/file/LZ9CEICL#3rcqvbmLAnWvqYZIKrYKNFGYF-gycRdDag7qChCE4Js (unfortunately too large for Github) and put it into the repository folder.

Afterwards should install Python 3 and the required libraries:

```
pip install -r requirements.txt
```

Then you should put you ebook in this folder, open the edit_epub.py file and edit the FILE_NAME and OUTPUT_FILE varibles so that they match the book you want to convert. Then you should execute the edit_epub.py file.

### Acknowledgements
The data is sourced from the English Wiktionary, the SQLite database containing it has been constructed on the base of Tatu Ylonen's parsed Wiktionary that can be found kaikki.org. 

If you have feedback or suggestions, please tell me. I have only tested it for some ebooks, so there could be bugs left.