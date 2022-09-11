import os

for i in os.listdir('dll-sources'):
    if i.endswith('.cpp'):
        print(f'Compiling {i} for Windows...')
        os.system(f'g++ --share dll-sources/{i} -o dlls/{i[:-4]+".dll"}')
        print(f'Compiling {i} for Linux & Unix...')
        os.system(
            f'wsl g++ --share dll-sources/{i} -fPIC -o dlls/{i[:-4]+".so"}')
