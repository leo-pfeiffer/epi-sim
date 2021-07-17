# remove all pickled files from this directory
import os

DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    for file in os.listdir(DIR):
        if file.endswith('pkl'):
            os.remove(os.path.join(DIR, file))


if __name__ == '__main__':
    main()


