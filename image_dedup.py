from PIL import Image
from os import listdir, remove
from os.path import isfile, join
import imagehash, sys

PATH = sys.argv[1]

def main():
    f_hashes = []
    files = [ f for f in listdir(PATH) if isfile(join(PATH, f))]
    for f in files:
        image_hash = imagehash.average_hash(Image.open(PATH + f))
        if image_hash in f_hashes:
            remove(PATH + f)
        else:
            f_hashes.append(image_hash)
    
if __name__ == '__main__':
    main()