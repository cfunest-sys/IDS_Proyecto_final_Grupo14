from werkzeug.security import check_password_hash, generate_password_hash
from data.queries import get_profesor_by_email


def validate_profesor_credentials(email, password):
    profesor = get_profesor_by_email(email)
    if not profesor:
        return None

    if check_password_hash(profesor["password"], password):

        return profesor
    return None


def hash_password(password):
    return generate_password_hash(password)
