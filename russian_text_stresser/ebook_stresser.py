import subprocess
from os import path, listdir, remove, rename, walk
from os.path import isfile
from zipfile import ZipFile
from bs4 import BeautifulSoup
from shutil import make_archive, rmtree
from russian_text_stresser.text_stresser import RussianTextStresser

class EbookStresser:
    def __init__(self) -> None:
        self._extraction_path = "8d9bad5b43259c6ee27d9aadc7b832"
        self._text_stresser = RussianTextStresser()
        #TODO: download the file dynamically and maybe remove this stuff here entirely
        #if not isfile(database_path):
        #    print("Unpacking db...")
        #    with ZipFile("russian_dict.zip", "r") as dbfile:
        #        dbfile.extractall()

    def convert_txt(self, input_txt_path: str, output_txt_path: str):
        if not input_txt_path.lower().endswith("txt") or not output_txt_path.lower().endswith("txt"):
            raise ValueError("TXT files should be supplied!")
        with open(input_txt_path, "r", encoding="utf-8") as input, open(output_txt_path, "w+", encoding="utf-8") as output:
            text = input.read()
            stressed_text = self._text_stresser.stress_text(text)
            output.write(stressed_text)

    def convert_book(self, input_file_path: str, output_file_path: str):
        
        if input_file_path.lower().endswith(".txt"):
            self.convert_txt(input_file_path, output_file_path)
            return
        elif not input_file_path.lower().endswith(".epub"):
            output_path = input_file_path.rsplit(".", 1)[0] + ".epub"
            print("Converting " + input_file_path + " to " + output_path)
            subprocess.run(["ebook-convert", input_file_path, output_path])
            input_file_path = output_path

        #if not ANALYZE_GRAMMAR:
        #    nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")

        with ZipFile(input_file_path, "r") as zip_ref:
            zip_ref.extractall(self._extraction_path)

        for subdir, dirs, files in walk(self._extraction_path):
            for file in files:
                filepath = path.join(subdir, file)
                if filepath.endswith(".xhtml") or filepath.endswith(".html"): 
                    print(filepath)
                    with open(filepath, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f.read(), "lxml")
                        for text_object in soup.find_all(text=True):
                            text: str = text_object.text
                            result_text = self._text_stresser.stress_text(text)
                            text_object.string.replace_with(result_text)
                    with open(filepath, "w+", encoding="utf-8") as f:
                        f.write(str(soup))
                    continue
                else:
                    continue

        make_archive(output_file_path, "zip", self._extraction_path)
        try:
            remove(output_file_path)
        except:
            pass
        rename(output_file_path + ".zip", output_file_path)
        rmtree(self._extraction_path)
    
    def convert_book_folder(self, input_folder_path: str, output_folder_path: str):
        for filename in listdir(input_folder_path):
            if filename.endswith(".epub"):
                self.convert_book(path.join(input_folder_path, filename), path.join(output_folder_path, filename))