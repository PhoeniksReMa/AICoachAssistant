import datetime
from django.utils import timezone
from rest_framework import serializers

from .models import OpenAIAssistant, OpenAIThread, TelegramUser




class OpenAIAssistantSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели OpenAIAssistant,
    где created_at — просто IntegerField.
    """
    instructions = serializers.CharField(allow_blank=True)

    class Meta:
        model = OpenAIAssistant
        # Указываем ровно те поля, что есть в модели
        fields = [
            'id',
            'object',
            'created_at',
            'name',
            'description',
            'model',
            'instructions',
            'tools',
            'metadata',
            'top_p',
            'temperature',
            'response_format',
        ]
        read_only_fields = ['object']

class OpenAIThreadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели OpenAIThread:
    {
      "id": "thread_abc123",
      "object": "thread",
      "created_at": 1698107661,
      "metadata": { ... }
    }
    """

    # Поле “object” по умолчанию равно "thread", можно сделать его read-only
    object = serializers.CharField(read_only=True)

    class Meta:
        model = OpenAIThread
        fields = [
            "id",
            "object",
            "created_at",
            "metadata",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор потока (например, \"thread_abc123\")"},
            "created_at": {"required": False, "allow_null": True},
            "metadata": {"required": False},
        }