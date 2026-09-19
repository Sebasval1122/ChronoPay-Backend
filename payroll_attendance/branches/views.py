from rest_framework import viewsets

from .models import Branch
from .serializers import BranchSerializer


class BranchViewSet(viewsets.ModelViewSet):
    """CRUD de branches."""

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
