from os import remove, rename
import os
import subprocess
import shutil, errno


def copy_folder(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:  # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise


if __name__ == "__main__":
    # Change working directory to the folder containing this script

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Print the current working directory
    print("Current working directory: {}".format(os.getcwd()))
    STRESSER_FOLDER = "russian_text_stresser"
    RELEASE_FOLDER_NAME = "../Stress-Marker-win"
    # SPACY_FOLDER_NAME = STRESSER_FOLDER + "/ru_core_news_sm-3.4.0"
    SPACY_FOLDER_NAME = "ru_core_news_sm-3.4.0"
    # RUSSIAN_DICT_NAME = STRESSER_FOLDER + "/russian_dict.db"
    RUSSIAN_DICT_NAME = "russian_dict.db"

    # subprocess.run(["pyinstaller",  STRESSER_FOLDER + "/gui.spec", "--noconfirm"])
    subprocess.run(["pyinstaller", "gui.spec", "--noconfirm"])
    try:
        shutil.rmtree(RELEASE_FOLDER_NAME)
    except Exception as e:
        print(e)
        pass
    copy_folder("dist/gui", RELEASE_FOLDER_NAME)
    # copy_folder(SPACY_FOLDER_NAME, RELEASE_FOLDER_NAME + "/" + SPACY_FOLDER_NAME)
    rename(
        RELEASE_FOLDER_NAME + "/gui.exe", RELEASE_FOLDER_NAME + "/#Stress marker.exe"
    )
    # Make dir russian_text_stresser in release folder if it doesn't exist
    if not os.path.exists(RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER):
        os.mkdir(RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER)

    shutil.copy(RUSSIAN_DICT_NAME, RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER)

    try:
        remove(RELEASE_FOLDER_NAME + ".zip")
    except:
        pass

    # Delete the build folder
    shutil.rmtree("dist")
    shutil.rmtree("build")
    shutil.make_archive(RELEASE_FOLDER_NAME, "zip", RELEASE_FOLDER_NAME)
