from os import remove, rename
import subprocess
import shutil, errno

def copy_folder(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise

if __name__ == "__main__":
    RELEASE_FOLDER_NAME = "Stress-Marker-win"
    SPACY_FOLDER_NAME = "ru_core_news_sm-3.1.0"
    RUSSIAN_DICT_NAME = "russian_dict.db"
    subprocess.run(["pyinstaller",  "gui.spec", "--noconfirm"])
    try:
        shutil.rmtree(RELEASE_FOLDER_NAME)
    except:
        pass
    copy_folder("dist/gui", RELEASE_FOLDER_NAME)
    copy_folder(SPACY_FOLDER_NAME, RELEASE_FOLDER_NAME + "/" + SPACY_FOLDER_NAME)
    rename(RELEASE_FOLDER_NAME + "/gui.exe", RELEASE_FOLDER_NAME + "/#Stress marker.exe")
    shutil.copy(RUSSIAN_DICT_NAME, RELEASE_FOLDER_NAME)
    try:
        remove(RELEASE_FOLDER_NAME + ".zip")
    except:
        pass
    shutil.make_archive(RELEASE_FOLDER_NAME, "zip", RELEASE_FOLDER_NAME)