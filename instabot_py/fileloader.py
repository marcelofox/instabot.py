import datetime
from instabot_py.persistence.manager import PersistenceManager
from instabot_py.config import config



persistence = PersistenceManager(config.get('database'))

f = open("/Users/marcelomendes/Projetos/instabot.py/followersList.txt", "r")
for x in f:
    data = x.replace('\n','').split(' - ')
    print("id: " + data[0])
    print("user: " + data[1])
    persistence.insert_username_last_year(user_id=data[0], username=data[1], followed_from_bot=0, create_date=datetime.datetime(2018, 5, 29))

#followers = persistence.get_all_followers()

#for f in followers:
#    print(f.username)
#    print(f.id)
#    print(f.followed_from_bot)
#    print(f.created)
