import asyncio
import aiohttp
import json
import logging
from datetime import datetime

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

good_code = 200

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, filename="logging.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

# Основные действия скрипта
async def main():
    async with aiohttp.ClientSession(url) as session:
        # Авторизация + получение токена
        logging.info('Authorization Request')
        try:
            async with session.post(login_check, json=user_json) as resp:
                logging.info(f'Authorization Response status: {resp.status}')
                assert resp.status == good_code, "Authorization fail"
                temp = await resp.json()
                token = temp['response']['token']
                logging.info(f'Authorization access pass, token: {token}')   
        except Exception as error:
            logging.critical(f'Authorization error: {error}')

        # Создание группы
        logging.info('Group add Request')
        try:
            async with session.post(group, json=group_add_json, headers={'Authorization': f'Bearer {token}'}) as resp:
                logging.info(f'Group add Response status: {resp.status}')
                assert resp.status == good_code, "Group add fail"
                temp = await resp.json()
                group_id = temp['response']['id']
                logging.info(f'Group add pass, Group id: {group_id}') 
        except Exception as error:
            logging.error(f'Group add error: {error}')

        # Создание плеера
        logging.info('Player add Request')
        try:
            async with session.post(player, json=player_add_json, headers={'Authorization': f'Bearer {token}'}) as resp:
                logging.info(f'Player add Response status: {resp.status}')
                assert resp.status == good_code, "Player add fail"
                temp = await resp.json()
                player_id = temp['response']['id']
                logging.info(f'Player add pass, Player id: {player_id}')
        except Exception as error:
            logging.error(f'Player add error: {error}')

        # Изменение ID группы
        try:
            player_add_json['mediaGroup'] = group_id
        except Exception as error:
            logging.error(f'Group id error: {error}')

        # Добавление плеера в группу    
        logging.info('Player add to Group Request')
        try:
            async with session.put(player, params={'id': player_id}, json=player_add_json, headers={'Authorization': f'Bearer {token}'}) as resp:
                logging.info(f'Player add to Group Response status: {resp.status}')
                assert resp.status == good_code, "Player add to Group fail"
                logging.info(f'Player add to Group pass, Player id: {player_id}, Group id: {group_id}')
        except Exception as error:
            logging.error(f'Player add to Group error: {error}')

        # Удаление плеера
        logging.info('Player delete Request')
        try:
            async with session.delete(player, params={'id': player_id}, headers={'Authorization': f'Bearer {token}'}) as resp:
                logging.info(f'Player delete Response status: {resp.status}')
                assert resp.status == good_code, "Player delete fail"
                logging.info('Player delete pass')
        except Exception as error:
            logging.error(f'Player delete error: {error}')

        # Удаление группы
        logging.info('Group delete Request')
        try:
            async with session.delete(group, params={'id': group_id}, headers={'Authorization': f'Bearer {token}'}) as resp:
                logging.info(f'Group delete Response status: {resp.status}')
                assert resp.status == good_code, "Group delete fail"
                logging.info('Group delete pass')
        except Exception as error:
            logging.error(f'Group delete error: {error}')

asyncio.run(main())