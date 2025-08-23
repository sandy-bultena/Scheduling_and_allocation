import os
import sys

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))


def main():
    try:
        from presenter.allocation_manager import AllocationManager
        AllocationManager(bin_dir=bin_dir)
    except Exception as e:
        print()
        print("==================================================================")
        print("ERROR:")
        print("==================================================================")
        print(e)
        print()
        print("==================================================================")
        print("System info")
        print("==================================================================")
        print(sys.version)
        print(sys.version_info)
        print()
        print()
        _=input("press enter to continue")


if __name__ == "__main__":
    main()


