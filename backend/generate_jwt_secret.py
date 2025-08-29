import random
import string

chars = string.ascii_letters + string.digits
secret = ''.join(random.choice(chars) for _ in range(32))
print(secret)
