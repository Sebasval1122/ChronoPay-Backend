from rest_framework.throttling import AnonRateThrottle


class RegistroEmpresaThrottle(AnonRateThrottle):
    scope = "registro_empresa"
    rate = "5/hour"

    def get_rate(self):
        return self.rate
