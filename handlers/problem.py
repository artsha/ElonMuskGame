from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("addproblem"))
async def add_problem(message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.answer("Использование: /addproblem текст проблемы")
        return
    
    problem_text = args[1].strip()
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("""
        SELECT r.room_id FROM rooms r 
        JOIN room_members rm ON r.room_id = rm.room_id 
        WHERE rm.user_id = ? AND r.status = 'lobby'
        ORDER BY rm.joined_at DESC LIMIT 1
    """, (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Добавлять проблемы можно только в лобби комнаты")
        return
    
    room_id = room[0]
    await db.execute("INSERT INTO problems (room_id, problem_text, added_by) VALUES (?, ?, ?)", 
                     (room_id, problem_text, user_id))
    await db.commit()
    await db.close()
    
    await message.answer("Проблема добавлена в банк")
