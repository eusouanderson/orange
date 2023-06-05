import os
from random import randint

random = randint(1, 5)
path = os.getcwd()+f'/src/BG/{random}.jpg'

print(path)
