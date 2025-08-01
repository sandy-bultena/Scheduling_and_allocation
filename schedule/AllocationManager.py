import os
import sys

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))

from presenter.allocation_manager import AllocationManager

def main():
    AllocationManager(bin_dir=bin_dir)


if __name__ == "__main__":
    main()


