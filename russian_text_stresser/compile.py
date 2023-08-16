from os import remove, rename
import os
import subprocess
import shutil, errno

# This is for publishing the app as executable on Windows

def copy_folder(src: str, dst: str) -> None:
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
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
    SPACY_FOLDER_NAME = "ru_core_news_sm-3.6.0"
    # RUSSIAN_DICT_NAME = STRESSER_FOLDER + "/russian_dict.db"
    RUSSIAN_DICT_NAME = "russian_dict.db"
    SIMPLE_CASES_NAME = "simple_cases.pkl"

    # subprocess.run(["pyinstaller",  STRESSER_FOLDER + "/gui.spec", "--noconfirm"])
    subprocess.run(["pyinstaller", "merged.spec", "--noconfirm"])
    try:
        shutil.rmtree(RELEASE_FOLDER_NAME)
    except Exception as e:
        print(e)
        pass
    copy_folder("dist/gui", RELEASE_FOLDER_NAME)
    copy_folder("dist/app", RELEASE_FOLDER_NAME)
    # copy_folder(SPACY_FOLDER_NAME, RELEASE_FOLDER_NAME + "/" + SPACY_FOLDER_NAME)
    rename(
        RELEASE_FOLDER_NAME + "/gui.exe", RELEASE_FOLDER_NAME + "/#Stress marker.exe"
    )
    rename(
        RELEASE_FOLDER_NAME + "/app.exe", RELEASE_FOLDER_NAME + "/#Chrome extension server.exe"
    )
    # Make dir russian_text_stresser in release folder if it doesn't exist
    if not os.path.exists(RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER):
        os.makedirs(RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER)

    shutil.copy(RUSSIAN_DICT_NAME, RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER)
    shutil.copy(SIMPLE_CASES_NAME, RELEASE_FOLDER_NAME + "/" + STRESSER_FOLDER)

    try:
        remove(RELEASE_FOLDER_NAME + ".zip")
    except:
        pass

    # Delete the build folder
    shutil.rmtree("dist")
    shutil.rmtree("build")
    shutil.make_archive(RELEASE_FOLDER_NAME, "zip", RELEASE_FOLDER_NAME)
