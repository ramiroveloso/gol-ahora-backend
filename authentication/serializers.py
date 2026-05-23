# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Usuario, Profesor


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'rol', 'telefono', 'direccion', 'activo'
        ]
        read_only_fields = ['id']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'rol', 'telefono', 'direccion'
        ]

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user


class ProfesorSerializer(UsuarioSerializer):
    alumnos_count = serializers.SerializerMethodField()

    class Meta(UsuarioSerializer.Meta):
        model = Profesor
        fields = UsuarioSerializer.Meta.fields + ['certificacion_deportiva', 'alumnos', 'alumnos_count']
        
    def get_alumnos_count(self, obj):
        return obj.alumnos.count()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
