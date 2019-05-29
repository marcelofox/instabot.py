from instabot_py.persistence.manager import PersistenceManager
from instabot_py.config import config


persistence = PersistenceManager(config.get('database'))

f = open("/home/fvd_jsouza/pworkspace/followersReaderJson/followersList.txt", "r")
for x in f:
    data = x.replace('\n','').split(' - ')
    print("id: " + data[0])
    print("user: " + data[1])
    persistence.insert_username(user_id=data[0], username=data[1], followed_from_bot=0)