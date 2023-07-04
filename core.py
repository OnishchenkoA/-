from datetime import datetime 
from pprint import pprint 
from vk_api.exceptions import ApiError

import vk_api

from config import acces_token



class VkTools():
    def __init__(self, acces_token):
       self.vkapi = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        
        try:
            info, = self.vkapi.method('users.get',
                                     {'user_id': user_id,
                                      'fields': 'city,bdate,sex,relation,home_town'
                                     }
                                     )
        except ApiError as e:
            info = {}
            print (f'error = {e}')
            
        user_info = {'name': (info['first_name'] + ' '+ info['last_name']) if 
                     'first_name' in info and 'last_name' in info else None,
                     'id':  info.get('id'),
                     'bdate': info.get('bdate') if 'bdate' in info else None,
                     'home_town': info.get('home_town'),
                     'sex': info.get('sex'),
                     'city': info['city']['id']
                     } 
        return user_info
    
    def serch_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.vkapi.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                }
                            )
        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        
        return res

    def get_photos(self, user_id):
        photos = self.vkapi.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError:
            return []
        
        res1 = []

        for photo in photos:
            res1.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res1.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res1[:2]


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(258264578)
    users = bot.serch_users(params, 100)
    pprint(bot.get_photos(users[2]['id']))