import hashlib
import random
import time


class Generator:

    def run_generator(self, t) -> None:

        start = time.time()
        count = 0
        previous_output = 'Aliens are real!'.encode()
        while count < t:
            previous_output = hashlib.sha256(
                previous_output).hexdigest().encode()
            count += 1
        end = time.time()
        print(
            f"It took {int((end - start) * 1000)} ms to calculate t={t} steps of hashing")
