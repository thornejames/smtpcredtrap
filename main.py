import ssl
import warnings
import logging
import sys

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging
from aiosmtpd.smtp import SMTP, AuthResult


# Use conventional SMTP AUTH LOGIN prompts.
#
# aiosmtpd defaults to:
#   b"User Name\x00"
#   b"Password\x00"
#
# Some embedded devices disconnect when they receive those prompts.
SMTP.AuthLoginUsernameChallenge = b"Username:"
SMTP.AuthLoginPasswordChallenge = b"Password:"


def configure_logging():
    logger = logging.getLogger("mail.log")

    # Prevent duplicate handlers.
    if logger.handlers:
        return

    formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s] %(message)s"
    )

    file_handler = logging.FileHandler(
        "aiosmtpd.log",
        mode="a"
    )
    file_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stderr_handler)
    logger.setLevel(logging.DEBUG)


configure_logging()


class Authenticator:
    def __call__(
        self,
        server,
        session,
        envelope,
        mechanism,
        auth_data
    ):
        try:
            username = auth_data.login.decode(
                "utf-8",
                errors="replace"
            )

            password = auth_data.password.decode(
                "utf-8",
                errors="replace"
            )

            if session.peer:
                source_ip = session.peer[0]
                source_port = session.peer[1]
            else:
                source_ip = "unknown"
                source_port = "unknown"

            print(
                "\n"
                "----------------------------------------\n"
                "SMTP authentication received\n"
                "----------------------------------------"
            )
            print(f"Source:    {source_ip}:{source_port}")
            print(f"Mechanism: {mechanism}")
            print(f"Username:  {username}")
            print(f"Password:  {password}")
            print("----------------------------------------\n")

        except Exception as error:
            print(
                f"Unable to process authentication data: {error}",
                file=sys.stderr
            )

        # Reject authentication after recording the attempt.
        return AuthResult(
            success=False,
            handled=False
        )


# Load the certificate used for STARTTLS and implicit TLS.
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    certfile="cert.pem",
    keyfile="key.pem"
)

authenticator = Authenticator()


# Port 25: plaintext SMTP with optional STARTTLS.
controller_25 = Controller(
    Debugging(),
    hostname="0.0.0.0",
    port=25,
    authenticator=authenticator,
    auth_required=True,
    auth_require_tls=False,
    tls_context=ssl_context,
    require_starttls=False
)


# Port 587: SMTP submission with optional STARTTLS.
controller_587 = Controller(
    Debugging(),
    hostname="0.0.0.0",
    port=587,
    authenticator=authenticator,
    auth_required=True,
    auth_require_tls=False,
    tls_context=ssl_context,
    require_starttls=False
)


# Port 465: implicit TLS/SMTPS.
controller_465 = Controller(
    Debugging(),
    hostname="0.0.0.0",
    port=465,
    authenticator=authenticator,
    auth_required=True,
    auth_require_tls=False,
    ssl_context=ssl_context
)


controllers = [
    controller_25,
    controller_587,
    controller_465
]


with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    try:
        for controller in controllers:
            controller.start()

        print("SMTP listeners started:")
        print("  Port 25  - SMTP with optional STARTTLS")
        print("  Port 587 - SMTP with optional STARTTLS")
        print("  Port 465 - implicit TLS/SMTPS")
        print()

        input("Press Enter to stop the SMTP listeners...")

    except KeyboardInterrupt:
        print("\nStopping SMTP listeners...")

    finally:
        for controller in controllers:
            try:
                controller.stop()
            except Exception:
                pass
