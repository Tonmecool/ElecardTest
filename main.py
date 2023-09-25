import asyncio
import aiohttp
import json
import logging
from datetime import datetime

good_code = 200

now = datetime.now()

# Чтение и присвоение данных
with open('urls.json') as f:
    urls = json.load(f)
    url = urls['main_url']
    login_check = urls['login']
    group = urls['group']
    player = urls['player']

with open('user.json') as f:
    user_json = json.load(f)

with open('group_add.json') as f:
    group_add_json = json.load(f)
    group_add_json['name'] += datetime.now().strftime("%d/%m/%Y %H:%M:%S")

with open('player_add.json') as f:
    player_add_json = json.load(f)
    player_add_json['name'] += datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, filename="logging.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


# Авторизация + получение токена
async def authorization(session):
    try:
        async with session.post(login_check, json=user_json) as resp:
            logging.info(f'Authorization Response status: {resp.status}')
            assert resp.status == good_code, f"Authorization fail, Response: {resp.text()}"
            temp = await resp.json()
            token = temp['response']['token']
            logging.info(f'Authorization access pass, token: {token}')
            return token
    except Exception as error:
        logging.critical(f'Authorization error: {error}')


# Создание группы
async def create_group(session, token):
    try:
        async with session.post(group, json=group_add_json, headers={'Authorization': f'Bearer {token}'}) as resp:
            logging.info(f'Group add Response status: {resp.status}')
            assert resp.status == good_code, f"Group add fail, Response: {resp.text()}"
            temp = await resp.json()
            group_id = temp['response']['id']
            logging.info(f'Group add pass, Group id: {group_id}')
            return group_id
    except Exception as error:
        logging.error(f'Group add error: {error}')


# Удаление группы
async def delete_group(session, group_id, token):
    try:
        async with session.delete(group, params={'id': group_id}, headers={'Authorization': f'Bearer {token}'}) as resp:
            logging.info(f'Group delete Response status: {resp.status}')
            assert resp.status == good_code, f"Group delete fail, Response: {resp.text()}"
            logging.info('Group delete pass')
    except Exception as error:
        logging.error(f'Group delete error: {error}')


# Создание плеера
async def create_player(session, token):
    try:
        async with session.post(player, json=player_add_json, headers={'Authorization': f'Bearer {token}'}) as resp:
            logging.info(f'Player add Response status: {resp.status}')
            assert resp.status == good_code, f"Player add fail, Response: {resp.text()}"
            temp = await resp.json()
            player_id = temp['response']['id']
            logging.info(f'Player add pass, Player id: {player_id}')
            return player_id
    except Exception as error:
        logging.error(f'Player add error: {error}')


# Добавление плеера в группу
async def player_to_group(session, player_id, group_id, token):
    try:
        async with session.put(player, params={'id': player_id}, json=player_add_json,
                               headers={'Authorization': f'Bearer {token}'}) as resp:
            logging.info(f'Player add to Group Response status: {resp.status}')
            assert resp.status == good_code, f"Player add to Group fail, Response: {resp.text()}"
            logging.info(f'Player add to Group pass, Player id: {player_id}, Group id: {group_id}')
    except Exception as error:
        logging.error(f'Player add to Group error: {error}')


# Удаление плеера
async def delete_player(session, player_id, token):
    try:
        async with session.delete(player, params={'id': player_id},
                                  headers={'Authorization': f'Bearer {token}'}) as resp:
            logging.info(f'Player delete Response status: {resp.status}')
            assert resp.status == good_code, f"Player delete fail, Response: {resp.text()}"
            logging.info('Player delete pass')
    except Exception as error:
        logging.error(f'Player delete error: {error}')


# Основные действия скрипта
async def main():
    async with aiohttp.ClientSession(url) as session:
        logging.info('Authorization Request')
        token = await authorization(session)

        logging.info('Group add Request')
        group_id = await create_group(session, token)

        logging.info('Player add Request')
        player_id = await create_player(session, token)

        # Изменение ID группы
        try:
            player_add_json['mediaGroup'] = group_id
        except Exception as error:
            logging.error(f'Group id error: {error}')

        logging.info('Player add to Group Request')
        await player_to_group(session, player_id, group_id, token)

        logging.info('Player delete Request')
        await delete_player(session, player_id, token)

        logging.info('Group delete Request')
        await delete_group(session, group_id, token)


asyncio.run(main())
