from rest_framework.throttling import AnonRateThrottle


class CompanyRegistrationThrottle(AnonRateThrottle):
    scope = "registro_empresa"
    rate = "5/hour"

    def get_rate(self):
        return self.rate
