#!/usr/bin/python

from glob import glob
import os
import subprocess
import filecmp
import sys

NORMAL = '\x1b[0m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'

def run_good(latc_path, tests_path):
    for rel_filepath in sorted(glob(tests_path + '*.lat')):
        abs_filepath = os.path.abspath(rel_filepath)

        root, _ = os.path.splitext(abs_filepath)
        rel_root, _ = os.path.splitext(rel_filepath)

        # Compile
        compile_retcode = subprocess.call([latc_path, abs_filepath])

        if compile_retcode > 0:
            print('{} {}'.format(rel_root, RED + 'CE' + NORMAL))
            continue

        # Open input if it exists
        proc_stdin = open(root + '.input') if os.path.isfile(root + '.input') else None
        # Open tmp output
        with open(root + '.proc.output', 'w') as proc_output:
            proc = subprocess.Popen(
                ['lli', root + '.bc'],
                stdin=proc_stdin,
                stdout=proc_output,
                stderr=proc_output
            )
            proc.communicate()
        # Close input
        if proc_stdin is not None:
            proc_stdin.close()
        # Compare outputs
        if os.path.isfile(root + '.output'):
            same = filecmp.cmp(root + '.output', root + '.proc.output')
        else:
            same = os.path.getsize(root + '.proc.output') == 0
        print('{} {}\n'.format(rel_root,
            GREEN + 'OK' + NORMAL if same
            else YELLOW + 'WA' + NORMAL)
        )
        # Remove tmp output
        os.remove(root + '.proc.output')


def run_bad(latc_path, tests_path):
    for rel_filepath in sorted(glob(tests_path + '*.lat')):
        abs_filepath = os.path.abspath(rel_filepath)

        root, _ = os.path.splitext(abs_filepath)
        rel_root, _ = os.path.splitext(rel_filepath)

        # Compile
        compile_retcode = subprocess.call([latc_path, abs_filepath])

        print('{} {}\n'.format(rel_root,
            RED + 'no CE' + NORMAL if compile_retcode == 0
            else GREEN + 'CE' + NORMAL)
        )

def run_suite(latc_path, suite):
    for tests_path in sorted(glob(suite + '/*/good/')):
        run_good(latc_path, tests_path)
    for tests_path in sorted(glob(suite + '/*/bad/')):
        run_bad(latc_path, tests_path)

def main():
    if len(sys.argv) < 2:
        print('Usage: ./lattest.py PATH_TO_LATC [TEST_SUITE...]\n'
              'Example: ./lattest.py ../latc basic arrays\n'
              'If no TEST_SUITE specified, assuming usage of all test suites.\n')
        sys.exit(1)

    latc_path = sys.argv[1]
    suites = sys.argv[2:]
    if not len(suites):
        suites = ['basic', 'arrays', 'struct', 'objects1', 'objects2',
                  'garbage-collector', 'other']
    for suite in suites:
        run_suite(latc_path, suite)

if __name__ == "__main__":
    main()
