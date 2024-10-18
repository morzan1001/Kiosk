from src.email.email_controller import EmailController

email_controller = None

def initialize_email_controller(server: str, port: int, login: str, password: str):
    global email_controller
    email_controller = EmailController(
        smtp_server=server,
        smtp_port=port,
        login=login,
        password=password
    )