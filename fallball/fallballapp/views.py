from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Client, ClientUser, Reseller
from .serializers import (ClientSerializer, ClientUserSerializer,
                          ResellerSerializer)
from .utils import get_object_or_403


class ResellerViewSet(ModelViewSet):
    """
    ViewSet that manages resellers.
    Only admin token allows managing resellers
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ResellerSerializer
    queryset = Reseller.objects.all()

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return ModelViewSet.create(self, request, *args, **kwargs)
        return Response("Only superuser can create reseller", status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        """
        Method is overwritten in order to implement superuser check
        """
        if request.user.is_superuser:
            return ModelViewSet.list(self, request, *args, **kwargs)
        return Response("Only superuser can get resellers list", status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return ModelViewSet.retrieve(self, request, *args, **kwargs)
        return Response("Only superuser can get reseller information", status=status.HTTP_403_FORBIDDEN)


class ClientViewSet(ModelViewSet):
    """
    ViewSet which manages clients
    """
    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        Create new reseller client
        """
        if request.user.is_superuser:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        # Check if there is a free space for new client
        free_space = reseller.limit - reseller.get_usage()
        if free_space >= request.data['storage']['limit']:
            # Every client should belong to particular reseller
            request.data['reseller'] = reseller
            return ModelViewSet.create(self, request, *args, **kwargs)
        return Response("Reseller limit is reached", status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, **kwargs):
        """
        Return list of clients which owned by particular reseller
        """

        # If admin token is provided we just get reseller from the database
        # If reseller token is provided we need to check that clients are owned by this reseller
        if request.user.is_superuser:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        queryset = Client.objects.filter(reseller=reseller)
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Return particular client which owned by particular reseller
        """
        if request.user.is_superuser:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        return ModelViewSet.retrieve(self, request, *args, **kwargs)

    @detail_route(methods=['get'])
    def reset(self, request, *args, **kwargs):
        """
        Recreate client to initial state
        """
        if request.user.is_superuser:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        # Before repairing objects to initial state
        # it needs to delete current objects
        client = get_object_or_404(Client, pk=kwargs['pk'])
        ClientUser.objects.filter(client=client).delete()
        client.delete()

        return Response("Client has been repaired", status=status.HTTP_200_OK)

class ClientUserViewSet(ModelViewSet):
    """
    Create new client user
    """
    queryset = ClientUser.objects.all().order_by('-id')
    serializer_class = ClientUserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Redefine regex in order to get user email as id
    lookup_value_regex = '[^@]+@[^@]+\.[^@]+'

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        # get client to provide it for user creation
        client = Client.objects.filter(reseller=reseller, pk=kwargs['client_pk']).first()
        if client:
            # Check if client has free space for new user
            free_space = client.limit - client.get_usage()
            if free_space >= request.data['storage']['limit']:
                request.data['client'] = client.id
                return ModelViewSet.create(self, request, *args, **kwargs)
            return Response('Client limit is reached', status=status.HTTP_400_BAD_REQUEST)
        return Response('Current reseller does not have permissions for this client', status=status.HTTP_403_FORBIDDEN)

    def list(self, request, **kwargs):
        if request.user.is_superuser:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            reseller = get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        client = get_object_or_404(Client, reseller=reseller, pk=kwargs['client_pk'])
        queryset = ClientUser.objects.filter(client=client)
        serializer = ClientUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_superuser:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'])
        else:
            get_object_or_403(Reseller, pk=kwargs['reseller_pk'], owner=request.user)

        return ModelViewSet.retrieve(self, request, *args, **kwargs)
