import json
import requests
from datetime import datetime


class Vkontakte:
    URL = 'https://api.vk.com/method/'

    def __init__(self, token, _id, version='5.131'):
        self.__params = {
            'access_token': token,
            'v': version,
        }
        self.id = _id

    def get_photos(self):
        print("Поиск фотографий в VK")
        url = self.URL + 'photos.get'
        params = {
            'owner_id': self.id,
            'album_id': 'wall',
            'extended': '1'
        }
        res = requests.get(url, params={**self.__params, **params})
        if res.status_code == 200:
            return res.json()
        else:
            print(f'Фотографии не найдены. Ошибка: {res.status_code}')

    def five_photos(self):
        five_photos = {}
        sort_photos = sorted(self.get_photos()['response']['items'],
                             key=lambda x: (x['sizes'][6]['width'] + x['sizes'][6]['height']), reverse=True)
        likes = set()

        for photo in sort_photos[:5]:
            name = photo['likes']['count']
            if name in likes:
                name = f'{name}, {datetime.utcfromtimestamp(photo["date"]).strftime("%Y-%m-%d")}'
            else:
                likes.add(name)
            size = photo['sizes'][6]
            five_photos[size['url']] = {'likes': name, 'size': f"{size['width']}X{size['height']}"}

        return five_photos


class YandexDisc:
    base_host = "https://cloud-api.yandex.net/"

    def __init__(self, token):
        self.__headers = {
            "Authorization": f"OAuth {token}"
        }

    def upload_from_internet(self, url, yandex_path, name):
        uri = "v1/disk/resources/upload"
        params = {"path": f'{yandex_path}/{name}', "url": url}
        response = requests.post(self.base_host + uri, headers=self.__headers, params=params)
        if response.status_code == 202:
            print(f"Фото загружено")
        else:
            print(f'Фото не загружено. Ошибка: {response.status_code}')

    def folder_creation(self, path):
        uri = "v1/disk/resources/"
        params = {"path": path}
        response = requests.get(self.base_host + uri, headers=self.__headers, params=params)
        if response.status_code == 404:
            response = requests.put(self.base_host + uri, headers=self.__headers, params=params)
            if response.status_code == 201:
                print(f"Создана папка {path.split('/')[-1]}")
        elif response.status_code != 200:
            print(f"Не удалось создать папку. Ошибка: {response.status_code}")


def write_logs(val):
    with open(f'photos_{id}.json', 'w') as file:
        json.dump(val, file, indent=0)


def backup_photos(photos: dict):
    data = []
    ya.folder_creation(folder)
    print('Начало загрузки фотографий')
    for url, values in photos.items():
        name = str(values['likes']) + '.jpg'
        ya.upload_from_internet(url, folder, name)
        data.append({"file_name": name, "size": values['size']})
    write_logs(data)
    print('Загрузка фотографий завершена')


id = input('Введите ID пользователя "ВКонтакте" ')
YD = input('Введите токен Яндекс Диска ')
folder = '/VK'
with open('token_vk.txt') as token:
    vk_token = token.read()
vk = Vkontakte(vk_token, id)
ya = YandexDisc(YD)

backup_photos(vk.five_photos())
