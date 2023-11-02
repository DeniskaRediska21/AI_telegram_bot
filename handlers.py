from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
import g4f

router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Hello!")

@router.message(F.text)
async def message_handler(msg: Message):
    
    ans = g4f.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{'role':'user','content':msg.text}])
    await msg.answer(f"{ans}")
