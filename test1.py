from decouple import config

def test_email_config():
    email_host = config("EMAIL_HOST")
    email_port = config("EMAIL_PORT", cast=int)
    email_user = config("EMAIL_HOST_USER")
    email_password = config("EMAIL_HOST_PASSWORD")
    
    print(f"EMAIL_HOST: {email_host} (type: {type(email_host)})")
    print(f"EMAIL_PORT: {email_port} (type: {type(email_port)})")
    print(f"EMAIL_HOST_USER: {email_user} (type: {type(email_user)})")
    print(f"EMAIL_HOST_PASSWORD: {email_password} (type: {type(email_password)})")

if __name__ == "__main__":
    test_email_config()
