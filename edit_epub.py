import subprocess
from russian_dictionary import RussianDictionary
from os import path, listdir, remove, rename, walk
from os.path import isfile
from spacy import load
from argparse import ArgumentParser
from zipfile import ZipFile
from bs4 import BeautifulSoup
from shutil import make_archive, rmtree

from text_stresser import RussianTextStresser

def convert_txt(input_txt_path: str, output_txt_path: str):
    ts = RussianTextStresser()
    if not input_txt_path.lower().endswith("txt") or not output_txt_path.lower().endswith("txt"):
        raise ValueError("TXT files should be supplied!")
    with open(input_txt_path, "r", encoding="utf-8") as input, open(output_txt_path, "w+", encoding="utf-8") as output:
        text = input.read()
        stressed_text = ts.stress_text(text)
        print(stressed_text)
        output.write(stressed_text)

def convert_book(input_file_path: str, output_file_path: str):

    if not isfile("russian_dict.db"):
        print("Unpacking db...")
        with ZipFile("russian_dict.zip", "r") as dbfile:
            dbfile.extractall()
    
    if input_file_path.lower().endswith(".txt"):
        convert_txt(input_file_path, output_file_path)
        return
    elif not input_file_path.lower().endswith(".epub"):
        output_path = input_file_path.rsplit(".", 1)[0] + ".epub"
        print("Converting " + input_file_path + " to " + output_path)
        subprocess.run(["ebook-convert", input_file_path, output_path])
        input_file_path = output_path

    ANALYZE_GRAMMAR = True

    extract_dir = "extract_dir_9580"
    
    #if not ANALYZE_GRAMMAR:
    #    nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")
    ts = RussianTextStresser()

    with ZipFile(input_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    for subdir, dirs, files in walk("extract_dir_9580"):
        for file in files:
            filepath = path.join(subdir, file)
            if filepath.endswith(".xhtml") or filepath.endswith(".html"): 
                print(filepath)
                with open(filepath, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "lxml")
                    for text_object in soup.find_all(text=True):
                        text: str = text_object.text
                        result_text = ts.stress_text(text)
                        text_object.string.replace_with(result_text)
                with open(filepath, "w+", encoding="utf-8") as f:
                    f.write(str(soup))
                continue
            else:
                continue


    make_archive(output_file_path, "zip", extract_dir)
    try:
        remove(output_file_path)
    except:
        pass
    rename(output_file_path + ".zip", output_file_path)
    rmtree(extract_dir)

def convert_book_folder(input_folder_path: str, output_folder_path: str):
    for filename in listdir(input_folder_path):
        if filename.endswith(".epub"):
            convert_book(path.join(input_folder_path, filename), path.join(output_folder_path, filename))

if __name__ == "__main__":
    parser = ArgumentParser(description='Add stress to Russian ebooks.')
    parser.add_argument('-input', type=str,
                       help='the input file')
    parser.add_argument('-output', type=str, help='the output file', default="output.epub")
    parser.add_argument('-input_folder', type=str, help='for batch processing: the input folder')
    parser.add_argument('-output_folder', type=str, help='for batch processing: the output folder')

    args = parser.parse_args()
    
    if args.input == None and args.input_folder == None:
        print("Please provide an input file!")
        quit()
    elif args.input != None and args.input_folder != None:
        print("Please specify either an input file or an input folder!")
        quit()
    if args.input != None:
        print(args.input)
        print(args.output)
        convert_book(args.input, args.output)
    elif args.input_folder != None and args.output_folder != None:
        convert_book_folder(args.input_folder, args.output_folder)    
