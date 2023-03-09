from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response


# serializers
from apps.resources.api.serializers.receipt import ProofPaymentSerializer, ProofResourcePaymentSerializer


class ProofPaymentViewSet(GenericViewSet):
    serializer_class = ProofPaymentSerializer

    def get_queryset(self, pk=None, resource_pk=None):
        if pk is not None:
            return self.get_serializer().Meta.model.objects.filter(id=pk, state=True).first()
        if resource_pk is not None:
            return self.get_serializer().Meta.model.objects.filter(state=True, resource=resource_pk)
        return self.get_serializer().Meta.model.objects.filter(state=True)
    
    def list(self, request):
        resource = request.GET.get('resource')
        queryset = self.get_queryset(resource_pk=resource)
        if queryset:
            serializer = ProofResourcePaymentSerializer(queryset, many=True)
            return Response({'items': serializer.data, 'messge': 'Consulta satisfactoria.'}, status=status.HTTP_200_OK)
        return Response({'message': 'No se encontraron archivos.'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'items': serializer.data, 'message': 'Comprobante subido correctamente.'}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors, 'message': 'No se pudo subir el comprobante correctamente.'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        queryset = self.get_queryset(pk)
        if queryset:
            serializer = self.serializer_class(queryset, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({ 'items': serializer.data, 'message': 'Comprobante actualizado correctamente.' }, status=status.HTTP_202_ACCEPTED)
            return Response({ 'error': serializer.errors , 'message': 'No se ha actualizao el comprobante correctamente.' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({ 'message': 'El comprobante no se encontró.'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset(pk)
        if queryset:
            queryset.delete()
            return Response({'message': 'Comprobante eliminado correctamente.'}, status=status.HTTP_202_ACCEPTED)
        return Response({'error': 'El comprobante ya fue eliminado anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)
