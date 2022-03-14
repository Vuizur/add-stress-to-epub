# Russian word stresser for ebooks

<!--![Add stress GUI screenshot](imgs/screenshot.png) ![A stressed ebook](imgs/ebook.png)
-->
<p float="left">
  <img src="imgs/screenshot.png" width="55%" />
  <img src="imgs/ebook.png" width="44%" /> 
</p>
(Screenshots of the GUI and a created ebook with stress marks)

(If you want to know how to use this with a dictionary for reading ebooks, [check out my tutorial!](https://github.com/Vuizur/add-stress-to-epub/wiki/How-to-read-books-in-Russian-with-stress-marks-and-interactive-dictionary-lookup))

This program stresses entire Russian ebooks and adds the dots over the ё. It not only is the most sophisticated open source stress detection tool (that I am aware of), it also allows you to convert entire ebooks!

To reach the best results, it analyzes the case and part of speech of every word in order to find the correct stress. So it will stress the word "слова" differently in these two sentences: `В стро́гом смы́сле сло́ва?` vs. `Твои́ слова́ ничего́ не зна́чат.`

### Installation

**For windows**, you simply need to download the [executable release](https://github.com/Vuizur/add-stress-to-epub/releases/download/v1.1/Stress-Marker-win.zip), unpack the .zip file into a folder and start the program called #Stress marker.exe. This opens up a GUI and you can simply select the ebook you want to convert. Click on the start processing button to start it all.

(If your ebook is not in the epub format, you need to install [Calibre](https://calibre-ebook.com/). If you have it installed, the script will automatically convert the book (for example from FB2) to epub)

I did not create executables for Linux or Mac, for these systems you should refer to the steps under "Command line use"

### Command line use

First you need to download the [dictionary zip file](https://github.com/Vuizur/add-stress-to-epub/releases/download/v1.0.1/russian_dict.zip).

Then you should download the Github repository (click the Code -> Download ZIP button) and put the dictionary zip file into this folder.

Afterwards should install [Python 3](https://www.python.org/downloads/) (and check the installer option to add it to PATH). Afterwards install the required libraries by executing following command in the command line (which can be opened in Windows Explorer through the "File" button at the top left and then selecting "Open Windows Powershell"):

```
pip install -r requirements.txt
```

Then you can simply execute the GUI by calling:

```
pip install PyQt6
python gui.py
```

If you want to use the command line utility, you should put you ebook in this folder and start the program with following command (and change input.epub to the file name of the ebook you want to convert):

```
python edit_epub.py -input "input.epub" -output "output.epub"
```

That's it!

You can also convert entire folders filled with epub files:
```
python edit_epub.py -input_folder "to-convert" -output_folder "was-converted"
```
If you have feedback or suggestions, please tell me. I have only tested it for some ebooks, so there could be bugs left. If you find a word that is being stressed incorrectly or if a word is on (English) Wiktionary but still not being stressed, then open an issue. I will maybe maintain a list of words that confuse the algorithm (pretty rare but happens), so that there is rather no stress than a wrong one.

If you are interested in modifying the program: The database used in this project has been created using my other project here: https://github.com/Vuizur/ebook_dictionary_creator 

### Limitations
In some cases the stress is omitted because there are multiple options the word could be stressed depending on the context (in the case of замок or все vs всё) or because they don't appear in my current data source, which can be the case for very rare words. Or the grammatical analysis delivered wrong results, which can also happen in rare cases.

### Acknowledgements
The data is sourced from the English Wiktionary, the SQLite database containing it has been constructed on the base of Tatu Ylonen's parsed Wiktionary that can be found kaikki.org. An additional data source is the OpenRussian project.

### The future
I so far have not found a good source for the Russian Wiktionary data and use the English Wiktionary data instead. The Wiktextract project will likely try to extract Russian entries somewhere in the next months or so, so I'll add this data once it is available.

### Similar projects

* Russiangram/Morpher(https://russiangram.com/, https://morpher.ru/accentizer/), closed source and connected to a paid program, also performs a grammatical analysis, I don't know if it also uses Wiktionary or another data source. I did not benchmark mine thoroughly against it, but in some cases mine seems to give better results, for example when копье is in prepositional case or also for the word дверном. Maybe Russiangram has a larger vocabulary though.

* Someone who implemented a similar program (without grammar analysis), but never published it: https://www.reddit.com/r/russian/comments/8akdm4/reading_and_the_problem_of_stress/ 
