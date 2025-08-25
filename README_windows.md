## Windows

### Python Installation

Go to [python site](https://www.python.org/) and navigate to the `Downloads` page

<img src="./python_download.png" alt="image-20250823111349808" style="zoom:33%;" />

Follow instructions for standard install

* Select admin privileges if you have them, 
* Select `add Python to path`
* PAY VERY CLOSE ATTENTION TO WHERE IT IS INSTALLED!!

<img src="./python_install.png" style="zoom:50%;" />



### Validation

Open a `cmd` window (got to windows search bar and type `cmd`)

<img src="./python_command_prompt.png" style="zoom:50%;" />

In the command window, type `where python`

<img src="./python_verify_version.png" style="zoom:75%;" />

The first version of python should be the one you just installed.  

If the above does not show the version of python that you installed, modify the path by...

* Open a `cmd` window
* Type `setx "c:\Users\SandyLocal\AppData\Local\Programs\Python\Python313\python.exe;%PATH"` **but** use the location where *you* saved the the `python.exe` file.

Validate again.

> NOTE: if the above doesn't work, all is not lost, but the easiest method is to ask your administrator to adjust the PATH environment variables on your computer to point to the correct location of python

## Application Installation

Download zip file to your machine (it will be located in your downloads folder)

<img src="./app_download_windows.png" style="zoom:50%;" />

Copy this file to your Desktop (drag'n'drop, or cut'n'paste)

<img src=".\app_zip_on_desktop_windows.png" style="zoom:50%;" />

Extract the files from the zip files by right clicking the zipped folder and selecting "Extract All"

<img src="./app_extract_files.png" style="zoom:50%;" />

Which will result in a new folder on your desktop

<img src="./app_unzipped_windows.png" style="zoom:50%;" />

At this point you can remove the zip file

## Running the program(s)

Open the Scheduling Folder and double click whichever program (Scheduler or Allocation) that you wish to run

![](./app_windows.png)