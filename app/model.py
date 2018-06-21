from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from .flask_mistune_pygments import markdown




class BaseModel(object):
    """
    创建时间几乎是所有模块都有的，所以定一个基类
    """
    creat_time = db.Column(db.DateTimem, default=datetime.now)
    # onupdate用来记录每次更新的时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)




# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(128), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     body_html = db.Column(db.Text)
#     create_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     update_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     author = db.Column(db.String(128), db.ForeignKey('user.id'))
#
#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         target.body_html = markdown(value)
#
#     def __repr__(self):
#         return self.title
#
#
# db.event.listen(Post.body, 'set', Post.on_changed_body)


#　多对多需要建立第三张表，　表示多对多的关系
# 用户的关注的新闻列表
user_collection = db.Table(
    "tb_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("tb_user.id"), primary_key=True),
    db.Column("article_id", db.Integer, db.ForeignKey("tb_article.id"), primary_key=True),
    db.Column("create_time", db.DateTime, default=datetime.now)
)

user_follow = db.table(
    "tb_user_follow",
    db.Column("follower_id", db.Integer, db.ForeignKey("tb_user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("tb_user.id"), primary_key=True),
)







class User(BaseModel, db.Model):
    """定义用户类"""
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    signature = db.Column(db.String(512), nullable=True)
    avatar_url = db.Column(db.String(256))
    # 性别枚举
    gender = db.Column(
        db.Enum(
            "MAN",
            "WOMAN"
        ),
        default="MAN")
    last_login = db.Column(db.DateTime, default=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)

    # 用户的收藏文章---多对多模型
    colletion_articles = db.relationship("Article", secondary=user_collection, lazy="dynamic")

    # 用户关注---自关联多对多
    followers = db.relationship("User",
                                secondary=user_follow,
                                # c在这里表示字段的意思，表示对应表里的follwed_id字段
                                primaryjoin=id == user_follow.c.follwed_id,
                                # c在这里表示字段的意思，表示对应表里的follower_id字段
                                secondaryjoin=id == user_follow.c.follower_id,
                                backref=db.backref("followed", lazy="dynamic"),
                                lazy="dynamic")
    # 自己写的文章
    article_list = db.relationship("Article", backref="user", lazy="dynamic")

    #　property属性可以让方法像属性一样使用
    @property
    def password(self):
        """
        直接拿取密码的时候告诉，当前密码是不可得到的
        :return: 提醒
        """
        raise AttributeError("当前属性不可读")


    @password.setter
    def password(self, value):
        """
        密码加密
        :param value: 真实密码
        :return:
        """
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        """
        数据库查到的密码与本次输入的密码加密后进行比较　检查密码是否正确
        :param password: 数据库查到的密码
        :return: bool值
        """
        return check_password_hash(self.password_hash, password)

    # 定义一个方法用来输出对象内容

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "user_name": self.user_name,
            "signature": self.signature,
            "avatar_url": self.avatar_url,
            "gender": self.gender if self.gender else "MAN",
            "followers_count": self.followers.count(),
            "article_count": self.article_list.count()
        }
        return resp_dict

    # 定义一个方法用来给后台拿到需要的用户数据
    def to_admin_dict(self):
        resp_dict = {
            "id": self.id,
            "user_name": self.user_name,
            "register_time": self.creat_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S")
        }
        return resp_dict

class Base_Article(object):
    """定义文章基类"""
    pass



class Free_Article(BaseModel, Base_Article, db.Model):
    """定义关于自由主题的文章模型类"""
    pass

class Work_Article(BaseModel, Base_Article, db.Model):
    """定义关于拼搏主题的文章模型类"""
    pass

class Thinking_Article(BaseModel, Base_Article, db.Model):
    """定义关于宁静主题的文章模型类"""
    pass



class Base_Categories(object):
    """定义各个主题分类的基类"""

class Free_Categories(BaseModel, Base_Categories, db.Model):
    """定义自由主题分类信息"""
    pass


class Work_Categories(BaseModel, Base_Categories, db.Model):
    """定义拼搏主题分类信息"""
    pass


class Thinking_Categories(BaseModel, Base_Categories, db.Model):
    """定义宁静主题分类信息"""
    pass



class Base_Comment(object):
    """定义评论基类"""
    pass

class Free_Comment(BaseModel, Base_Comment, db.Model):
    """定义自由主题的评论模型类"""
    pass

class Work_Comment(BaseModel, Base_Comment, db.Model):
    """定义拼搏主题的评论模型类"""
    pass

class Thinking_Comment(BaseModel, Base_Comment, db.Model):
    """定义宁静主题的评论模型类"""
    pass



class Base_CommentLike(object):
    """定义点赞基类"""
    pass

class Free_Comment_like(BaseModel, Base_Comment, db.Model):
    """定义自由主题点赞模型类"""
    pass

class Work_Comment_like(BaseModel, Base_Comment, db.Model):
    """定义拼搏主题点赞模型类"""
    pass

class Thinking_Comment_like(BaseModel, Base_Comment, db.Model):
    """定义宁静主题点赞模型类"""
    pass










# @login_manager.user_loader
# def user_loader(id):
#     return User.query.get(int(id))

