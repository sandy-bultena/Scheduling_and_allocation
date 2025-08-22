import os
import sys

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))

from presenter.allocation_manager import AllocationManager
a=input("press enter to continue")
print(sys.version)
print(sys.version_info)

def main():
    a=input("press enter to continue")
    try:
        AllocationManager(bin_dir=bin_dir)
    except Exception as e:
        print(e)
    a=input("press enter to continue")


if __name__ == "__main__":
    main()


