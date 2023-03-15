

def check_auth(info):
    """
    A function to check authorization.
    """
    user = info.context.user
    if user.is_anonymous:
        raise Exception("Not logged in!")