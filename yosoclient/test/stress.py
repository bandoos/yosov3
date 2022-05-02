from yosoclient.config import ClientConfig
from yosoclient.core import Client
from multiprocessing import Pool
from uuid import uuid4
import os
import shutil
import sys
from time import perf_counter
from itertools import chain
from numpy import mean, std

test_image = "./images/apple.jpg"
stress_images_dir = "./stress_test_images"


def copy_to_rand_path(source: str, dest_dir: str):
    _, ext = os.path.splitext(source)
    new_name = str(uuid4()) + ext
    new_path = os.path.join(dest_dir, new_name)
    shutil.copy(source, new_path)
    return new_path


def worker(times=20):
    res = []
    for i in range(times):
        config = ClientConfig()
        client = Client(config)
        path = copy_to_rand_path(test_image, stress_images_dir)
        tic = perf_counter()
        resp = client.predict_request(path)
        toc = perf_counter()
        elaps = toc - tic
        print(f"Requedst took: {elaps:0.4f} seconds")
        res.append(elaps)
    return res


if __name__ == "__main__":

    n_procs = int(sys.argv[1])

    if not os.path.exists(stress_images_dir):
        os.mkdir(stress_images_dir)

    with Pool(processes=n_procs) as p:
        ress = p.map(worker, [20] * 5)

    res = list(chain(ress))

    print(mean(res), "+-", std(res), "sec")
