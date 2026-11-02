from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("room"))
async def room_menu(message: Message):
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("""
        SELECT r.room_id, r.creator_id, r.status 
        FROM rooms r 
        JOIN room_members rm ON r.room_id = rm.room_id 
        WHERE rm.user_id = ? 
        ORDER BY rm.joined_at DESC LIMIT 1
    """, (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Ты не состоишь ни в одной комнате\n/create - создать\n/join ID - присоединиться")
        return
    
    room_id, creator_id, status = room
    is_creator = user_id == creator_id
    
    async with db.execute("SELECT COUNT(*) FROM room_members WHERE room_id = ?", (room_id,)) as cursor:
        members_count = (await cursor.fetchone())[0]
    
    async with db.execute("SELECT COUNT(*) FROM problems WHERE room_id = ? AND used = 0", (room_id,)) as cursor:
        problems_count = (await cursor.fetchone())[0]
    
    await db.close()
    
    text = "Комната: " + str(room_id) + "\n"
    text += "Игроков: " + str(members_count) + "\n"
    text += "Проблем в банке: " + str(problems_count) + "\n"
    text += "Статус: " + str(status) + "\n\n"
    
    text += "Общие команды:\n"
    text += "/players - список игроков\n"
    text += "/addproblem текст - добавить проблему\n\n"
    
    if is_creator:
        text += "Команды создателя:\n"
        text += "/startround - начать раунд\n"
        text += "/endround - завершить раунд\n"
        text += "/deleteroom - удалить комнату и завершить игру\n"
    
    await message.answer(text)
