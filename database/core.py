from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base, User, QuestionMapping
from sqlalchemy import select

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def check_subscriber(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на уведомления"""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        
        if user and user.early_access:
            return True
        return False

async def get_all_subscribers():
    """Получает список всех подписчиков для рассылки"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.early_access == True)
        )
        subscribers = result.scalars().all()
        return subscribers

async def save_question_mapping(admin_message_id: int, user_id: int):
    """Сохраняет связь между сообщением админа и пользователем"""
    async with async_session() as session:
        mapping = QuestionMapping(
            admin_message_id=admin_message_id,
            user_id=user_id
        )
        session.add(mapping)
        await session.commit()

async def get_user_by_admin_message(admin_message_id: int):
    """Получает user_id по ID сообщения в админ-чате"""
    async with async_session() as session:
        result = await session.execute(
            select(QuestionMapping).where(QuestionMapping.admin_message_id == admin_message_id)
        )
        mapping = result.scalars().first()
        return mapping.user_id if mapping else None

async def add_subscriber(user_id: int, username: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        
        if user:
            user.early_access = True
            user.username = username
        else:
            new_user = User(user_id=user_id, username=username, early_access=True)
            session.add(new_user)
        
        await session.commit()