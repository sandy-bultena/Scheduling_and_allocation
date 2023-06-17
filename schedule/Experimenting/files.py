import os

path_to_file = "xxx.txt"
if os.access(path_to_file, os.W_OK):
    print("ok")
else:
    print("nok")
with open(path_to_file,"w") as f:
    f.write("hello")
