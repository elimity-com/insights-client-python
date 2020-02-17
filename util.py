import random
import string

# https://stackoverflow.com/a/2030081/4667966
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))