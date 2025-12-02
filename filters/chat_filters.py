from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import ADMIN_CHAT_ID

class NotAdminChatFilter(BaseFilter):
    """Фильтр, который пропускает только сообщения НЕ из админ-чата"""
    
    async def __call__(self, message: Message) -> bool:
        return message.chat.id != ADMIN_CHAT_ID
