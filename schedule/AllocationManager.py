import os
import sys

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))

from presenter import AllocationManager

def main():
    AllocationManger(bin_dir=bin_dir)


if __name__ == "__main__":
    main()


