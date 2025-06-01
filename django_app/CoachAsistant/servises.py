import os

from .models import OpenAIThread, TelegramUser, OpenAIAssistant
from .serializers import OpenAIAssistantSerializer, OpenAIThreadSerializer

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class OpenAIAssistantService:
    def create_assistant(self):
        api_response = client.beta.assistants.create(
            instructions="",
            name="CoachAssistant",
            model="gpt-4o-mini"
        )

        serializer = OpenAIAssistantSerializer(data=api_response.dict())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

class OpenAIThreadService:
    def __init__(self, assistant_id=None, thread_id=None):
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def create_thread(self, message_text: str, vector_store_id: list):
        api_response = client.beta.threads.create(
                messages=[{"role": "user", "content": message_text}],
                # tool_resources={
                #     "file_search": {
                #         "vector_store_ids": vector_store_id
                #     }
                # }
            )
        serializer = OpenAIThreadSerializer(data=api_response.dict())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.thread_id = serializer.data.get('id')
        return serializer


    def  add_message_tread(self, user_text: str):
        return client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=user_text
            )

    def run_tread(self):
        return client.beta.threads.runs.create_and_poll(
        thread_id=self.thread_id,
        assistant_id=self.assistant_id
    )

    def clear_tread(self, chat_id):
        try:
            user = TelegramUser.objects.get(chat_id=chat_id)
            client.beta.threads.delete(user.thread.id)
            user.thread.delete()
            return 'Ok'
        except Exception as e:
            return str(e)


class TelegramUserService:
    '''
    Сервис для работы с моделью TelegramUser через сериализатор.
    '''
    def __init__(self, **kwargs):
        self.chat_id = kwargs.get("chat_id")

    def create_user(self, assistant_id, thread_id):
        user = TelegramUser.objects.create(
            chat_id=self.chat_id,
            assistant_id=assistant_id,
            thread_id=thread_id
        )
        user.save()
        return

    def get_user(self):
        return TelegramUser.objects.get(chat_id=self.chat_id)

    def get_thread_by_user(self):
        try:
            user = TelegramUser.objects.get(pk=self.chat_id)
            thread = user.thread  # здесь – связанный OpenAIThread
            return thread
        except TelegramUser.DoesNotExist:
            return None