# Russian word stresser for ebooks in epub format

The aim of this program is to stress entire Russian ebooks and to add the dots over the ё. If your ebook is not in the epub format, I would recommend to use Calibre to convert it beforehand.

Right now the program stresses the large majority of words, although sometimes the stress is omitted because a) there are multiple options the word could be stressed depending on the context or case (in the case of замок or все vs всё or чем vs чём) or b) simply because they don't appear in my current data source, which can be the case for very rare words. The goal of this tool is that you can be sure - if a word is stressed - that it will be pronounced that way.

### Installation

First you should download the Github repository (the Code -> Download ZIP button).

Afterwards should install Python 3 (and check the installer option to add it to PATH). Afterwards install the required libraries by executing following command in the command line (which can be opened in Windows Explorer through the "File" button at the top left and then selecting "Open Windows Powershell"):

```
pip install -r requirements.txt
```

Then you should put you ebook in this folder and start the program with following command (and change input.epub to the file name of the ebook you want to convert):

```
python edit_epub.py -input "input.epub" -output "output.epub"
```

### Acknowledgements
The data is sourced from the English Wiktionary, the SQLite database containing it has been constructed on the base of Tatu Ylonen's parsed Wiktionary that can be found kaikki.org. An additional data source is the OpenRussian project.

If you have feedback or suggestions, please tell me. I have only tested it for some ebooks, so there could be bugs left.