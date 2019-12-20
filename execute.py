#!/usr/bin/env python3
import os
from multiprocessing import Pool

if __name__ == "__main__":
    processes = ('./app/copy.py', './app/paste.py')

    def run_process(processo):
        os.system('python {}'.format(processo))

    pool = Pool(processes=2)
    pool.map(run_process, processes)
