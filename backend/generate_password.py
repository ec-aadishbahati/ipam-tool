import random
import string

uppercase = string.ascii_uppercase
lowercase = string.ascii_lowercase
digits = string.digits
special = '!@#$%^&*'

password_parts = [
    random.choice(uppercase),
    random.choice(lowercase), 
    random.choice(digits),
    random.choice(special)
]

all_chars = uppercase + lowercase + digits + special
for _ in range(12):  # 16 total - 4 required = 12 random
    password_parts.append(random.choice(all_chars))

random.shuffle(password_parts)
password = ''.join(password_parts)
print(password)
