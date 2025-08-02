import os
import sys

from schedule.gui_pages.allocation_manager_tk import AllocationManagerTk
bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))
c = AllocationManagerTk("Hi",bin_dir = bin_dir)
c.start_event_loop()