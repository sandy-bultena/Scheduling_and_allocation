# =================================================================================================================
# to create scripts that can be downloaded via pip install - requires a python installation
# =================================================================================================================
# NOTE: if you don't already have the password, ask the maintainer of this code for it
# ~/Documents/pypi_test_token.txt
#
# Change the version number in pyproject.toml
# install 'build' and twine if you don't already have them
# from the Scheduling_and_allocation-PythonWithoutDB directory (i.e. from the directory where the .toml file is

python3 -m build
python3 twine upload dist/*


# =================================================================================================================
# to create an executable folder that needs no python installer
# =================================================================================================================
# NOTE: this is OS dependent, so must be done for each OS that you wish to have an installer for
#
# run these commands from the 'src' directory, the result will be in the 'dist' directory
# copy one of the executables into the other's directory, zip and give to user
python -m pip install pyinstaller  # or python3 if on mac

python -m PyInstaller SchedulerProgram.py   --icon scheduler_icon.ico   --add-binary scheduling_and_allocation/schedule_logo.png:scheduling_and_allocation --add-binary scheduling_and_allocation/schedule_ico.png:scheduling_and_allocation --add-binary scheduling_and_allocation/modified_tk/Images/:scheduling_and_allocation/modified_tk/Images/ --add-data scheduling_and_allocation/export/view_template.tex:scheduling_and_allocation/export/ --add-binary scheduling_and_allocation/allocation_ico.png:scheduling_and_allocation/ --add-binary scheduling_and_allocation/allocation_logo.png:scheduling_and_allocation/

python -m PyInstaller AllocationManager.py --icon allocation_icon.ico  --add-binary scheduling_and_allocation/schedule_logo.png:scheduling_and_allocation --add-binary scheduling_and_allocation/schedule_ico.png:scheduling_and_allocation --add-binary scheduling_and_allocation/modified_tk/Images/:scheduling_and_allocation/modified_tk/Images/ --add-data scheduling_and_allocation/export/view_template.tex:scheduling_and_allocation/export/ --add-binary scheduling_and_allocation/allocation_ico.png:scheduling_and_allocation/ --add-binary scheduling_and_allocation/allocation_logo.png:scheduling_and_allocation/
