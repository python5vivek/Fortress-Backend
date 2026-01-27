from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {
            'password': {'write_only': True},
            "email":{"write_only":True},
            "id":{"read_only":True}
            }
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)