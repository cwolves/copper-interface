import zipfile
import os

# Path to your Python code directory
code_dir = "../cdk/lambdas/forwarder/"

# Path to the directory where you installed the libraries using `pip install -t`
libs_dir = "../cdk/lambdas/forwarder/libs"

# Name of the ZIP archive to create
zip_file = "lambda_forwarder.zip"

# Add your code files to the archive
zf = zipfile.ZipFile(zip_file, mode="w")
for foldername, subfolders, filenames in os.walk(code_dir):
    for filename in filenames:
        path = os.path.join(foldername, filename)
        zf.write(path, path[len(code_dir) + 1 :])

# Add the installed libraries to the archive
for foldername, subfolders, filenames in os.walk(libs_dir):
    for filename in filenames:
        path = os.path.join(foldername, filename)
        zf.write(path, path[len(libs_dir) + 1 :])

zf.close()
