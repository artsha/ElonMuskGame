from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("endround"))
async def end_round(message: Message):
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("SELECT room_id, current_problem FROM rooms WHERE creator_id = ? AND status = 'round'", (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Только создатель может завершить раунд, и раунд должен быть активен")
        return
    
    room_id, current_problem = room
    
    await db.execute("UPDATE problems SET used = 1 WHERE room_id = ? AND problem_text = ? AND used = 0", 
                     (room_id, current_problem))
    await db.execute("UPDATE rooms SET status = 'lobby', current_problem = NULL, elon_musk_user_id = NULL WHERE room_id = ?", 
                     (room_id,))
    
    await db.commit()
    await db.close()
    
    await message.answer("Раунд завершён. Проблема удалена из банка.\nМожно начать новый раунд: /startround")
