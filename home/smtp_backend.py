from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import smtplib

class CustomEmailBackend(EmailBackend):
    def open(self):
        """
        Version simplifiée de la méthode open pour Python 3.12
        """
        if self.connection:
            return False

        try:
            self.connection = smtplib.SMTP(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )

            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()  # Version simplifiée sans paramètres pour Python 3.12
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False  # Ajout d'un retour False en cas d'échec silencieux