import datetime
from django.db.models import Q

from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from psc.api.serializers import (
    CategorySerializer, CompanySerializer, AccountSerializer,
    InvitationSerializer, UserSerializer, NotificationSerializer,
    ProductSerializer
)

from psc.accounts.models import Account
from psc.companies.models import Company
from psc.notifications.models import Notification
from psc.product.models import Category, Product
from psc.taskapp.tasks import send_invitation_email
from psc.users.models import InvitationKey, User


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.get_account().user_set.all()

    @detail_route(methods=['post'], serializer_class=UserSerializer)
    def confirm(self, request, pk):
        user = User.objects.get(id=pk)
        user.confirmed = True
        user.save()
        return Response({'detail': 'User confirmed'})

    @detail_route(methods=['post'], serializer_class=UserSerializer)
    def make_owner(self, request, pk):
        user = User.objects.get(id=pk)
        user.access_level = User.ACCESS_LEVEL_OWNER
        user.save()
        return Response({'detail': 'User set as owner'})


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    class Meta:
        model = Category

    @list_route(methods=['get'], serializer_class=CategorySerializer)
    def top(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        return Response(self.get_serializer(categories, many=True).data)

    @detail_route(methods=['get'], serializer_class=CategorySerializer)
    def children(self, request, pk=None):
        try:
            category = Category.objects.get(id=pk)
            children = category.get_children()
        except Category.DoesNotExist:
            children = []

        return Response(self.get_serializer(children, many=True).data)

    def _get_nested_list(self, current, tree_list):
        if current:
            tree_item = list(Category.objects.filter(parent=current.parent))
            tree_list.append(tree_item)
            self._get_nested_list(current.parent, tree_list)
        return tree_list

    @detail_route(methods=['get'], serializer_class=CategorySerializer)
    def list_tree(self, request, pk=None):
        category = Category.objects.get(id=pk)
        tree_list = []
        self._get_nested_list(category, tree_list)
        response = []
        tree_list.reverse()
        for tree_list_item in tree_list:
            response.append(self.get_serializer(tree_list_item, many=True).data)
        return Response(response)


class CompanyViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    class Meta:
        model = Company


class AccountViewSet(ModelViewSet):

    serializer_class = AccountSerializer
    queryset = Account.objects.none()

    @list_route(methods=['POST'], serializer_class=AccountSerializer)
    def deactivate_account(self, request):
        account = request.user.get_account()
        account.is_active = False
        account.deleted_at = datetime.date.today()
        account.save()
        return Response({'detail': 'Account deactivated'})

    @list_route(methods=['POST'], serializer_class=AccountSerializer)
    def restore_account(self, request):
        account = request.user.get_account()
        account.is_active = True
        account.save()
        return Response({'detail': 'Account restored'})


class InvitationViewSet(mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = InvitationSerializer
    queryset = InvitationKey.objects.all()

    @detail_route(methods=['POST'], serializer_class=InvitationSerializer)
    def resend(self, request, pk):
        instance = InvitationKey.objects.get(id=pk)

        invite_key = InvitationKey.objects.create(
            email=instance.email,
            user=instance.user,
            created_at=datetime.date.today(),
            access_level=instance.access_level
        )

        InvitationKey.objects.filter(id=pk).delete()

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.META['HTTP_HOST']

        send_invitation_email(protocol, domain, invite_key.key, invite_key.email)

        return Response(InvitationSerializer(invite_key).data)


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer

    class Meta:
        madel = Notification

    def get_queryset(self):
        return Notification.objects.filter(
            Q(user__account=self.request.user.get_account()) |
            Q(user__owner=self.request.user.get_account())
        )

    @detail_route(methods=['post'], serializer_class=NotificationSerializer)
    def archivate(self, request, pk):
        notification = Notification.objects.get(id=pk)
        notification.status = Notification.STATUS_ARCHIVED
        notification.save()
        return Response(self.get_serializer(notification).data)

    @list_route(methods=['post'], serializer_class=NotificationSerializer)
    def make_read(self, request):
        self.get_queryset().filter(status=Notification.STATUS_NEW).update(
            status=Notification.STATUS_READ
        )
        return Response({'detail': "All new notifications mark as read"})


class ProductViewSet(mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
