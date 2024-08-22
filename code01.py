import asyncio
import random
import re
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMessageRequest

accounts = [
    {"name": "wirab", "phone": "+491702814038", "api_id": "21442333", "api_hash": "855169c5ce62c8b50cd58af0d66ff607", "button_text": "🌲 Forest"},
    {"name": "qmoru", "phone": "+4915236802221", "api_id": "23376010", "api_hash": "06d24bfa47dca003224249a7c86cd5c3", "button_text": random.choice(['🔼 Go North', '◀️ Go West'])},
    {"name": "qtude", "phone": "+380955548460", "api_id": "24709319", "api_hash": "3c1e3f0c2d1ff3e28b41c6e9ff3246ae", "button_text": random.choice(['🔼 Go North', '▶️️ Go East'])}
]

async def handle_message(client, message, account):
    """Обработка сообщения для нахождения числа и нажатия кнопки"""
    if message.text:
        # Изменение BUTTON_TEXT в зависимости от найденных иконок
        if '🌲' in message.text:
            account['button_text'] = '🌲 Forest'
        elif '🏔' in message.text:
            account['button_text'] = '🏔 Valley'
        elif '🌻' in message.text:
            account['button_text'] = '🌻 Field'
        elif '🔥' in message.text:
            if account["name"] == "qmoru":
                account['button_text'] = random.choice(['🔼 Go North', '◀️ Go West'])
            else:  # для qtude и wirab
                account['button_text'] = random.choice(['🔼 Go North', '▶️️ Go East'])

        # Проверка заряда батареи
        match = re.search(r'🔋(\d+)/', message.text)
        if match:
            number = int(match.group(1))
            if number > 0:
                # Ожидание произвольного времени перед отправкой сообщения
                await asyncio.sleep(random.uniform(1, 3))
                # Отправка сообщения с текстом кнопки
                await client(SendMessageRequest(
                    peer='@ChatWarsBot',
                    message=account['button_text']
                ))
                return True
    return False

async def send_command(client, account):
    """Отправка команды /me и обработка ответов"""
    chat = await client.get_entity('@ChatWarsBot')
    is_active = True

    while True:
        try:
            if is_active:
                # Отправка команды /me
                await client.send_message(chat, '/me')

                # Получение последних сообщений
                messages = await client.get_messages(chat, limit=5)

                # Проверка сообщений
                short_wait = False  # Флаг для определения короткого ожидания
                for message in messages:
                    if await handle_message(client, message, account):
                        if '🔥' in message.text:
                            short_wait = True
                        break

                # Ожидание произвольного времени
                if short_wait:
                    # Ожидание от 3.5 до 5 минут
                    await asyncio.sleep(random.uniform(3.5 * 60, 5 * 60))
                else:
                    # Ожидание от 180 до 420 минут
                    await asyncio.sleep(random.uniform(1 * 60, 3 * 60))

            # Проверка на наличие знаков - и +
            messages = await client.get_messages(chat, limit=5)
            for message in messages:
                if '-' in (message.text or ''):
                    is_active = False
                    print(f"{account['name']}: Найден знак '-', отправка команд приостановлена")
                    break
                elif '+' in (message.text or ''):
                    is_active = True
                    print(f"{account['name']}: Найден знак '+', отправка команд возобновлена")
                    break

            if not is_active:
                # Пауза при неактивности перед повторной проверкой
                await asyncio.sleep(random.uniform(1, 3))  # Пауза перед повторной проверкой

        except Exception as e:
            print(f"{account['name']}: Произошла ошибка: {e}")

async def main():
    """Запуск клиентов и отправка команд"""
    clients = []
    try:
        for account in accounts:
            client = TelegramClient(account["name"], account["api_id"], account["api_hash"])
            await client.start(account["phone"])
            clients.append(client)
        tasks = [send_command(client, account) for client, account in zip(clients, accounts)]
        await asyncio.gather(*tasks)
    finally:
        for client in clients:
            await client.disconnect()

# Запуск основной функции
asyncio.run(main())
