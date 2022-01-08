import os
for subdir, dirs, files in os.walk("extract_dir_9580"):
    for file in files:
        print(os.path.join(subdir, file))
