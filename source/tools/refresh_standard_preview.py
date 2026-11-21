#!/usr/bin/env python3
"""Explicitly refresh the shared visual preview from the reusable sample playlist."""
from pathlib import Path
import shutil
import tempfile
from compile_deck import SHARED_DECK, compile_playlist


def main():
    with tempfile.TemporaryDirectory(prefix='standard-preview-') as temporary:
        output = compile_playlist('kickoff-sample', Path(temporary).resolve() / 'deck')
        shutil.copy2(output / 'index.html', SHARED_DECK / 'index.html')
        for source in (output / 'assets').iterdir():
            shutil.copy2(source, SHARED_DECK / 'assets' / source.name)
    print('Refreshed shared preview from kickoff-sample source units.')


if __name__ == '__main__':
    main()
