import time
from lynx.consensus.epoch_context import EpochContext
from lynx.consensus.generator import Generator
from lynx.consensus.epoch_context import EpochContext
from eth.vm.forks.lynx.blocks import LynxBlock

# Command Line Arguments
# t: Amount of sequential steps required by generator
# Run this command for ~5 second delay: python3 test_generator.py --t 2500000


def test_generator():
    start = time.time()
    epoch = EpochContext(1, 1, 100, 10)

    num = Generator.start_generator(LynxBlock, epoch)
    end = time.time()
    print(f"{end - start} ms...")
    num2 = num + 1
    print(f"DONE, {time.time() - start} ms...")




if __name__ == "__main__":
    test_generator()
