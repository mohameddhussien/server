import re as Exp


def validate_username(username):
    if len(username) < 6:
        return "Username must be at least 6 characters long."
    if not str.isalnum(username):
        return "Username must contain only alphanumeric characters."
    return None


def validate_email(email):
    email_regex = Exp.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_regex.match(email):
        return "Invalid email address."
    return None


def validate_password(password):
    password_regex = Exp.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$")
    if not password_regex.match(password):
        return "Password must be at least 8 characters long. Contain at least one uppercase letter. One lowercase letter, and one number."
    return None


def validate_confirm_password(password, confirm_password):
    if password != confirm_password:
        return "Passwords must match."
    return None


def validate_signup_inputs(data):
    error = validate_username(data["username"])
    if error is not None:
        return error
    error = validate_email(data["email"])
    if error is not None:
        return error
    error = validate_password(data["password"])
    if error is not None:
        return error
    error = validate_confirm_password(data["password"], data["confirmpass"])
    if error is not None:
        return error
    return None
