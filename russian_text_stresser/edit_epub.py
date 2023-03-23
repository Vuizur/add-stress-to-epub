from ebook_stresser import EbookStresser
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(description="Add stress to Russian ebooks.")
    parser.add_argument("-input", type=str, help="the input file")
    parser.add_argument(
        "-output", type=str, help="the output file", default="output.epub"
    )
    parser.add_argument(
        "-input_folder", type=str, help="for batch processing: the input folder"
    )
    parser.add_argument(
        "-output_folder", type=str, help="for batch processing: the output folder"
    )

    args = parser.parse_args()

    ebook_stresser = EbookStresser()

    if args.input == None and args.input_folder == None:
        print("Please provide an input file!")
        quit()
    elif args.input != None and args.input_folder != None:
        print("Please specify either an input file or an input folder!")
        quit()
    if args.input != None:
        print(args.input)
        print(args.output)
        ebook_stresser.convert_book(args.input, args.output)
    elif args.input_folder != None and args.output_folder != None:
        ebook_stresser.convert_book_folder(args.input_folder, args.output_folder)
