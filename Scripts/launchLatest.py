# This script launches the latest version of the PopcornFX Editor. It looks in the Start Menu for the latest version and opens it.
import os

source_path = os.getenv('APPDATA')+'\Microsoft\Windows\Start Menu\Programs\Persistant Studios'

dirs = [name for name in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, name))]

max = max(dirs)
print(max)
os.startfile(f'{source_path}\\{max}\\{max} Editor.lnk')
