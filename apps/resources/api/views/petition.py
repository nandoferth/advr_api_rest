from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.db.utils import IntegrityError
# serializers
from apps.resources.api.serializers.petition import PetitionSerializers

from apps.resources.models import Petition
from apps.works.models import Work


class PetitionViewSet(GenericViewSet):

    serializer_class = PetitionSerializers

    def get_queryset(self, pk=None):
        return self.get_serializer().Meta.model.objects.filter(state=True, id=pk).first()

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'items': serializer.data, 'message': 'La petición ha tenido éxito.'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors, 'message': 'Petición no creada.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def verificar_peticiones(self, request):
        try:
            petitions = request.data['works']
            if(petitions):
                list_request = []
                for petition in petitions:
                    serializer = PetitionSerializers(data=petition)
                    if serializer.is_valid():
                        list_request.append(serializer.data)
                    else:
                        list_request.append({'error': serializer.errors})
                return Response({'items': list_request, 'message': 'Las peticiones fueron verificadas.'}, status=status.HTTP_207_MULTI_STATUS)
            return Response({'error': 'Consulta no satisfactoria', 'message': 'No se encontraron peticiones a solicitar.'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'error': { "works": ["Este campo es requerido." ]}}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': { "works": ["Se requiere una lista." ]}}, status=status.HTTP_400_BAD_REQUEST)

    def confirmar_peticiones(self, request):
        try:
            petitions = request.data['works']
            if(petitions):
                list_peticiones = []
                for petition_object in petitions:
                    petition = Petition(
                        work = Work.objects.filter(id = petition_object['work'], state = True).first(),
                        amount = petition_object['amount'],
                        method_pay = petition_object['method_pay'],
                        bank_data = petition_object['bank_data'],
                        beneficiary =petition_object['beneficiary'],
                        bank =petition_object['bank'],
                    )
                    list_peticiones.append(petition)
                ser = Petition.objects.bulk_create(list_peticiones)
                return Response({'items': ser, 'message': 'Las peticiones fueron creadas.'}, status=status.HTTP_207_MULTI_STATUS)   
            return Response({'error': 'Consulta no satisfactoria', 'message': 'No se encontraron peticiones a solicitar.'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as error:
            return Response({'error': str(error) }, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': { "works": ["Se requiere una lista." ]}}, status=status.HTTP_400_BAD_REQUEST)
        except Petition.work.RelatedObjectDoesNotExist:
            return Response({"error": { "work": [ "Clave primaria \"\" inválida - objeto no existe." ] }}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as error:
            return Response({"error": str(error) }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as error:
            return Response({"error": str(error) }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset(pk)
        if queryset:
            serializer = self.serializer_class(queryset, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'items': serializer.data, 'message': 'La actualización ha tenido éxito.'}, status=status.HTTP_200_OK)
            return Response({'error': serializer.errors, 'message': 'La actualización no ha tenido éxito.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'No se encontro la petición.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset(pk)
        if queryset:
            queryset.delete()
            return Response({'message': 'Solicitud de peticion eliminada correctamente.'}, status=status.HTTP_200_OK)
        return Response({'message': 'No se encontro la petición.'}, status=status.HTTP_404_NOT_FOUND)
