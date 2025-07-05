from werkzeug.security import generate_password_hash, check_password_hash

# helper fucntions


#password helper functions
def gen_hash(password):
    p = generate_password_hash(password)
    return p

def check_hash(h_password, password):
    status = check_password_hash(h_password, password)
    if status:
        return status
    else:
        return False