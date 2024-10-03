import secrets

#print(secrets.token_hex(10))

username = secrets.token_hex(10)

password = secrets.token_hex(20)

print(f"user: {username}")
print(f"password: {password}")
