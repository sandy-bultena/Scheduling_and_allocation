# this will create a directory in the dist folder.  Zip up and send to users

# run this command from the 'src' directory
pyinstaller SchedulerProgram.py --add-binary scheduling_and_allocation/schedule_logo.png:scheduling_and_allocation --add-binary scheduling_and_allocation/schedule_ico.png:scheduling_and_allocation --add-binary scheduling_and_allocation/modified_tk/Images/:scheduling_and_allocation/modified_tk/Images/ --add-data scheduling_and_allocation/export/view_template.tex:scheduling_and_allocation/export/ --icon scheduler_icon.ico
