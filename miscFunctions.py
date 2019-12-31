#
# Miscellaneous Functions
#

import random
import string

def generate_unique_id(stringLength=30):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
