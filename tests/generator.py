import argparse
from lynx.generator import Generator

# Command Line Arguments
# t: Amount of sequential steps required by generator
# Run this command for ~5 second delay: python3 test_generator.py --t 2500000

parser = argparse.ArgumentParser()
parser.add_argument('--t', type=int, required=True)
args = parser.parse_args()


def test_generator():
    generator = Generator()
    generator.run_generator(args.t)


if __name__ == "__main__":
    test_generator()
