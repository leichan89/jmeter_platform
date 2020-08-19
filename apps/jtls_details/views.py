from rest_framework import generics
from .serializer import JtlsDetailsSerializer
from .models import JtlsDetails


class RecordJtl(generics.CreateAPIView):

    queryset = JtlsDetails.objects.all()
    serializer_class = JtlsDetailsSerializer
