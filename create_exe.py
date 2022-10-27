import os
import PyInstaller.__main__

DIRPATH = os.path.dirname(os.path.realpath(__file__))
DIRNAME = DIRPATH.split('\\')[-1]

def build() -> None:
    PyInstaller.__main__.run([
        f'{DIRPATH}\\main.py',
        #'--clean',
        '-n', DIRNAME,
        '--onefile',
        '--noconfirm',
        '--log-level', 'WARN',
        '--hidden-import', 'pynput.keyboard._win32',
        '--hidden-import', 'pynput.mouse._win32',
        '--add-data', f'{DIRPATH}\\README.md;.',
        '--add-data', f'{DIRPATH}\\katatoRIOT.png;img',
        '--add-data', f'{DIRPATH}\\config\\config.ini;config',
        '-i', 'katatoRIOT.png',
        #'-n %CurrDirName%',
    ])

if __name__ == "__main__":
    build()