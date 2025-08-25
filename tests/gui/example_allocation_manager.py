import os
import sys



bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../../"))
from schedule.model import SemesterType
from schedule.gui_pages.allocation_manager_tk import AllocationManagerTk

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
print (os.path.join(bin_dir, "../../"))
logo_dir = os.path.join(bin_dir, "../../schedule")
c = AllocationManagerTk("Hi",bin_dir = logo_dir)
c.create_welcome_page([SemesterType.winter, SemesterType.fall, SemesterType.summer])
c.start_event_loop()