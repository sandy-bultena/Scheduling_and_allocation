import os
from Presentation.Scheduler import Scheduler

bin_dir: str = os.path.dirname(os.path.realpath(__file__))


def main():
    Scheduler(bin_dir)


if __name__ == "__main__":
    main()
