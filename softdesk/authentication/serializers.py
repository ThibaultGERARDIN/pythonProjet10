from .models import MyUser
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("id", "username", "age", "rgpd_consent")


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = ("username", "password", "password2", "date_of_birth", "rgpd_consent")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})

        return attrs

    def create(self, validated_data):
        user = MyUser.objects.create(
            username=validated_data["username"],
            date_of_birth=validated_data["date_of_birth"],
            rgpd_consent=validated_data["rgpd_consent"],
        )

        user.set_password(validated_data["password"])
        if user.age > 15:
            user.save()
        else:
            raise ValidationError("Vous devez avoir au moins 15ans pour vous inscrire.")

        return user
