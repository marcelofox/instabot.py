from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from instabot_py.persistence import PersistenceBase

Base = declarative_base()


class Follower(Base):
    __tablename__ = 'followers'
    id = Column(String, primary_key=True)
    username = Column(String)
    created = Column(DateTime, default=datetime.now())
    last_followed = Column(DateTime, default=datetime.now())
    unfollow_count = Column(Integer, default=0)
    followed_from_bot = Column(Integer,default=0)


class Media(Base):
    __tablename__ = 'medias'
    id = Column(String, primary_key=True)
    created = Column(DateTime, default=datetime.now())
    status = Column(Integer)
    code = Column(String)

class UserToFollow(Base):
    __tablename__ = "usertofollow"
    id = Column(String, primary_key=True)
    username = Column(String)
    created = Column(DateTime, default=datetime.now())


class Persistence(PersistenceBase):

    def __init__(self, connection_string):
        self._engine = create_engine(connection_string, echo=False)
        Base.metadata.create_all(self._engine)

        self._Session = sessionmaker(bind=self._engine)
        self._session = self._Session()

    def check_already_liked(self, media_id):
        """ controls if media already liked before """
        return self._session.query(Media) \
                   .filter(Media.id == media_id) \
                   .one_or_none() is not None

    def check_already_followed(self, user_id):
        """ controls if user already followed before """
        return self._session.query(Follower) \
                   .filter(Follower.id == user_id) \
                   .one_or_none() is not None

    def check_already_unfollowed(self, user_id):
        """ controls if user was already unfollowed before """
        return self._session.query(Follower) \
                   .filter(Follower.id == user_id) \
                   .filter(Follower.unfollow_count > 0) \
                   .one_or_none() is not None

    def insert_media(self, media_id, status):
        """ insert media to medias """
        media = Media(id=media_id, status=status)
        self._session.add(media)
        self._session.commit()

    def insert_possible_user(self, username, user_id,create_date):
        """ insert media to medias """
        user = UserToFollow(id=user_id, username=username,created=create_date)
        self._session.add(user)
        self._session.commit()
    
    def delete_from_possible_user(self,user_id):
        """ delete username """
        self._session.query(UserToFollow).filter(UserToFollow.id == user_id).delete()
        self._session.commit()
    
    def get_possible_username_random(self):
        """ Gets random username  """
        usertofollow = self._session.query(UserToFollow).order_by(func.random()).first()
        return usertofollow if usertofollow else None

    def check_if_possible_userid_exists(self, userid):
        """ Checks if username exists """
        return self._session.query(UserToFollow).filter(UserToFollow.id == userid).count()

    def get_usertofollow_row_count(self):
        """ Gets the number of usernames in table """

        return self._session.query(UserToFollow).count()   
        
        

    def insert_username(self, user_id, username, followed_from_bot):
        """ insert user_id to usernames """
        follower = Follower(id=user_id, username=username,followed_from_bot=followed_from_bot)
        self._session.add(follower)
        self._session.commit()
    
    def insert_username_last_year(self, user_id, username, followed_from_bot, create_date):
        """ insert user_id to usernames """
        follower = Follower(id=user_id, username=username,followed_from_bot=followed_from_bot,last_followed=create_date)
        self._session.add(follower)
        self._session.commit()

    def insert_unfollow_count(self, user_id=None, username=None):
        """ track unfollow count for new futures """

        if user_id:
            follower = self._session.query(Follower).filter(Follower.id == user_id).first()
        elif username:
            follower = self._session.query(Follower).filter(Follower.username == username).first()
        else:
            return

        follower.unfollow_count += 1
        self._session.commit()

    def get_username_random(self):
        """ Gets random username """
        follower = self._session.query(Follower).filter(Follower.unfollow_count == 0).filter(Follower.followed_from_bot > 0).order_by(func.random()).first()
        return str(follower.username) if follower else None

    def get_username_to_unfollow_random(self):
        """ Gets random username that is older than follow_time and has zero unfollow_count """
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=self.bot.follow_time)
        return self._session.query(Follower) \
            .filter(Follower.last_followed < cut_off_time).filter(Follower.unfollow_count == 0).filter(Follower.followed_from_bot > 0) \
            .order_by(func.random()).first()

    def get_username_row_count(self):
        """ Gets the number of usernames in table """

        return self._session.query(Follower).count()    

    def get_all_followers(self):
        """ Gets all followers from table """

        return self._session.query(Follower)
    
    def get_follower(self,user_id):
        """ Gets all followers from table """

        return self._session.query(Follower).filter(Follower.id == user_id).first()

    def get_medias_to_unlike(self):
        """ Gets random media id that is older than unlike_time"""
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=self.bot.time_till_unlike)

        media = self._session.query(Media) \
            .filter(Media.created < cut_off_time) \
            .filter(Media.status == 200) \
            .order_by(func.random()).first()

        return media.id if media else None

    def update_media_complete(self, media_id):
        """ update media to medias """
        media = self._session.query(Media) \
            .filter(Media.id == media_id).first()
        media.status = 201
        self._session.commit()

    def check_if_userid_exists(self, userid):
        """ Checks if username exists """
        return self._session.query(Follower).filter(Follower.id == userid).count()
