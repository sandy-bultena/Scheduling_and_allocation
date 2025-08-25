## MAC OS X

## Python Installation

Go to [python site](https://www.python.org/) and navigate to the `Downloads` page

<img src="./python_download_mac.png" alt="image-20250823111349808" style="zoom:33%;" />

Download python.

You should see an installation program icon in your task bar <img src="./python_app_image_icon.png" alt="image-20250823111819678" style="zoom:25%;" />

Double click this icon, and accept all default options.

Once installation is complete, you should see the following 'finder' window pop-up

<img src="./python_app_folder.png" alt="image-20250823112048447" style="zoom: 25%;" />

Double click the "update Shell" icon

### Validation

Use the search tool (Command-spacebar) open a terminal window

<img src="./search_terminal.png" alt="image-20250823110447048" style="zoom:33%;" />

Type the following in the terminal window

```bash
python3 --version
```

The version number should be the same python that you installed

<img src="./python_version_mac.png" alt="image-20250823112346490" style="zoom:33%;" />

### Install Dependencies

Use the search tool (Command-spacebar) open a terminal window

<img src="./search_terminal.png" alt="image-20250823110447048" style="zoom:33%;" />

Type the following in the terminal window

```bash
python3 -m pip install reportlab
```

```bash
python3 -m pip install pillow
```



## Application Installation

Download zip file to your Mac (it will be located in your downloads folder)

<img src="./mac_app_download.png" alt="image-20250823104546043" style="zoom:25%;" />

Copy this file to your Desktop (drag'n'drop, or cut'n'paste)

<img src="./app_zip_on_desktop.png" alt="image-20250823105546647" style="zoom:33%;" />

Double click the icon, and you will have a new icon on your desktop.  

<img src="./app_folder_on_desktop.png" alt="image-20250823105734689" style="zoom:33%;" />

At this point you can remove the zip file

## Running the program(s)

Use the search tool (Command-spacebar) open a terminal window

<img src="./search_terminal.png" alt="image-20250823110447048" style="zoom:33%;" />

Navigate to the correct directory

```bash
cd Desktop
cd Scheduling_and_allocation
```

<img src="./changing_dirs.png" alt="image-20250823110633980" style="zoom:33%;" />

Run either the scheduler or allocation program

```bash
python3 SchedulerProgram.py
```

<img src="./image-20250823111129921.png" alt="image-20250823111129921" style="zoom:33%;" />

```bash
python3 AllocationManager.py
```

<img src="./run_allocation_cmd_line.png" alt="image-20250823110943947" style="zoom:33%;" />