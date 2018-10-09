import time
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class PscTokens(PasswordResetTokenGenerator):

    def _num_days(self, dt):
        return int(time.time())

psc_tokens = PscTokens()
