from psc.accounts.models import Account
from psc.companies.models import Company
from psc.notifications.models import Notification
from psc.product.models import Category, Product
from rest_framework import serializers

from psc.users.models import InvitationKey, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'name')


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('owner', )
        read_only_fields = ('owner', )


class InvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvitationKey
        fields = ('email', 'user', 'id')
        read_only_fields = ('email', 'user', 'id')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')
        read_only_fields = ('id', 'username')


class NotificationSerializer(serializers.ModelSerializer):
    type_text = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('status', 'type_text', 'status_text', 'id')

    def get_type_text(self, obj):
        return obj.get_type_display()

    def get_status_text(self, obj):
        return obj.get_status_display()


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name')
