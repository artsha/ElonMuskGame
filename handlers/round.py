import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("startround"))
async def start_round(message: Message):
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("SELECT room_id, status FROM rooms WHERE creator_id = ? AND status = 'lobby'", (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Только создатель может начать раунд, и раунд можно начать только в лобби")
        return
    
    room_id, status = room
    
    async with db.execute("SELECT id, problem_text FROM problems WHERE room_id = ? AND used = 0", (room_id,)) as cursor:
        problems = await cursor.fetchall()
    
    if not problems:
        await db.close()
        await message.answer("В банке нет неиспользованных проблем")
        return
    
    problem_id, problem_text = random.choice(problems)
    
    async with db.execute("SELECT user_id FROM room_members WHERE room_id = ?", (room_id,)) as cursor:
        members = await cursor.fetchall()
    
    if len(members) < 2:
        await db.close()
        await message.answer("Нужно минимум 2 игрока")
        return
    
    elon_user = random.choice(members)[0]
    
    await db.execute("UPDATE rooms SET status = 'round', current_problem = ?, elon_musk_user_id = ? WHERE room_id = ?", 
                     (problem_text, elon_user, room_id))
    await db.commit()
    
    # Отправляем проблемы
    bot = message.bot
    for member in members:
        m_id = member[0]
        try:
            if m_id == elon_user:
                await bot.send_message(m_id, "Тема раунда: Elon Musk")
            else:
                await bot.send_message(m_id, f"Тема раунда: {problem_text}")
        except:
            pass
    
    await db.close()
    await message.answer("Раунд начат! Проблема разослана игрокам.")
