import os
import re, platform
O = platform.system().lower()


from Presentation import globals

image_dir : str = None
logo_file : str = None

def get_image_dir():
    """Gets the image directory"""
    global image_dir, logo_file
    
    if image_dir: return image_dir

    # replaces Perl checks to Allocation and Scheduler individually
    if globals.bin_dir: return os.path.join(globals.bin_dir, 'Tk', 'Images')

    # no longer used
    #pwd = os.getcwd()
    #_find(pwd, wanted)

    return image_dir

def get_logo():
    return os.path.join(globals.bin_dir, 'ScheduleLogo.gif')

def get_allocation_logo():
    return os.path.join(globals.bin_dir, 'AllocationLogo.gif')

# =================================
# NO LONGER USED
#   Searches the file system for the image directory
# =================================
def _find(pwd, callback):
    """Checks various directories for the images.
    ----
    - Parameter pwd => The first parent directory to start looking from
    - Parameter callback => The method to call to verify directory contents.
        - Parameters: root, subdirs, files
        - Raises Exception("found it") if condition successful
    """
    try:
        _walk(os.path.join(pwd, '..'), callback)
        
        # Windows
        if re.search('win', O): _walk(os.environ("TEMP"), callback)
        # else (incl. Mac OS & Linux)
        else: _walk(os.environ("HOME"), callback)
        
        # if default image not found,
        # search directories until found (shouldn't happen)
        while not image_dir and not logo_file:
            _walk(pwd, callback)

    except Exception as e:
        if str(e) != 'found it':
            os.chdir(pwd)
            raise e
    
    os.chdir(pwd)

def _walk(pwd, callback):
    """Wrapper for os.walk(), making it more similar to Perl's File::Find find()"""
    for v in os.walk(pwd): callback(*v)

def wanted(root, dirs, files):
    """Checks if the current directory has the correct images dir"""
    global image_dir
    if "Tk" in dirs and os.path.isdir(os.path.join(root, "Tk", "Images")):
        image_dir = os.path.join(root, "Tk", "Images")
        raise Exception("found it")

def wanted_logo(root, dirs, files):
    """Checks if the current directory has the logo"""
    global logo_file
    if "ScheduleLogo.gif" in files:
        logo_file = os.path.join(root, "ScheduleLogo.gif")
        raise Exception("found it")