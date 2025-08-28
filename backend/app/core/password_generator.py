import secrets
import string


def generate_secure_password(length: int = 16) -> str:
    """Generate cryptographically secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_admin_credentials():
    """Generate secure admin credentials for first-time setup"""
    username = "admin"
    password = generate_secure_password(20)
    email = f"admin@{secrets.token_hex(8)}.local"
    return username, password, email
