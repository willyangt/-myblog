from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

from app import db
from .flask_mistune_pygments import markdown




class BaseModel(object):
    """
    创建时间几乎是所有模块都有的，所以定一个基类
    """
    creat_time = db.Column(db.DateTime, default=datetime.now)
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
    db.Column("free_article_id", db.Integer, db.ForeignKey("tb_free_article.id"), primary_key=True),
    db.Column("work_article_id", db.Integer, db.ForeignKey("tb_work_article.id"), primary_key=True),
    db.Column("thinking_article_id", db.Integer, db.ForeignKey("tb_thinking_article.id"), primary_key=True),
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
                                primaryjoin=id == user_follow.c.followed_id,
                                # c在这里表示字段的意思，表示对应表里的follower_id字段
                                secondaryjoin=id == user_follow.c.follower_id,
                                backref=db.backref("followed", lazy="dynamic"),
                                lazy="dynamic")
    # 自己写的free主题的文章
    free_article_list = db.relationship("Free_Article", backref="user", lazy="dynamic")
    # 自己写的work主题的文章
    work_article_list = db.relationship("Work_Article", backref="user", lazy="dynamic")
    # 自己写的work主题的文章
    thinking_article_list = db.relationship("Thinking_Article", backref="user", lazy="dynamic")


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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    source = db.Column(db.String(64), default='个人发布')
    digest = db.Column(db.String(512), nullable=False)
    content = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(256))
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("tb_user.id"))
    status = db.Column(db.Integer, default=0)   # 0代表文章待审核，1代表通过，　-1代表拒绝通过
    reason = db.Column(db.String(256))  # 未通过原因


    # def to_review_dict(self):
    #     resp_dict = {
    #         "id": self.id,
    #         "title": self.title,
    #         "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    #         "status": self.status,
    #         "reason": self.reason if self.reason else ""
    #     }
    #     return resp_dict
    #
    # def to_basic_dict(self):
    #     resp_dict = {
    #         "id": self.id,
    #         "title": self.title,
    #         "source": self.source,
    #         "digest": self.digest,
    #         "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    #         "index_image_url": self.image_url,
    #         "clicks": self.clicks,
    #     }
    #     return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "content": self.content,
            "clicks": self.clicks,
            "image_url": self.image_url,
        }
        return resp_dict

# BaseModel = declarative_base()

class Free_Article(BaseModel, Base_Article, db.Model):
    """定义关于自由主题的文章模型类"""
    __tablename__ = "tb_free_article"
    # 共同的字段写在父类，　三个主题的分类信息不同，所以单独写入模型子类
    free_category_id = db.Column(db.ForeignKey("tb_free_category.id"))
    free_comments = db.relationship("Free_Comment", lazy="dynamic")

    def to_dict(self):
        base_resp_dict = super().to_dict()
        resp_dict = {
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "free_comments_count": self.free_comments.count(),
            "free_category": self.free_category.to_dict(),
            "author": self.user.to_dict() if self.user else None
        }
        #　将父类继承来的字典和子类自己实现的字典合并返回
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict


class Work_Article(BaseModel, Base_Article, db.Model):
    """定义关于拼搏主题的文章模型类"""
    __tablename__ = "tb_work_article"
    # 共同的字段写在父类，　三个主题的分类信息不同，所以单独写入模型子类
    work_category_id = db.Column(db.ForeignKey("tb_work_category.id"))
    work_comments = db.relationship("Work_Comment", lazy="dynamic")

    def to_dict(self):
        base_resp_dict = super().to_dict()
        resp_dict = {
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "work_comments_count": self.work_comments.count(),
            "work_category": self.work_category.to_dict(),
            "author": self.user.to_dict() if self.user else None
        }
        # 　将父类继承来的字典和子类自己实现的字典合并返回
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict

class Thinking_Article(BaseModel, Base_Article, db.Model):
    """定义关于宁静主题的文章模型类"""
    __tablename__ = "tb_thinking_article"
    # 共同的字段写在父类，　三个主题的分类信息不同，所以单独写入模型子类
    thinking_category_id = db.Column(db.ForeignKey("tb_thinking_category.id"))
    thinking_comments = db.relationship("Thinking_Comment", lazy="dynamic")

    def to_dict(self):
        base_resp_dict = super().to_dict()
        resp_dict = {
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "thinking_comments_count": self.thinking_comments.count(),
            "thinking_category": self.thinking_category.to_dict(),
            "author": self.user.to_dict() if self.user else None
        }
        # 　将父类继承来的字典和子类自己实现的字典合并返回
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict



class Base_Categories(BaseModel):
    """定义各个主题分类的基类"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    #定义分类表基类方法
    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name
        }

class Free_Categories(Base_Categories, db.Model):
    """定义自由主题分类信息"""
    __tablename__ = "tb_free_category"
    free_article_list = db.relationship("Free_Article", backref="free_category", lazy="dynamic")


class Work_Categories(Base_Categories, db.Model):
    """定义拼搏主题分类信息"""
    __tablename__ = "tb_work_category"
    work_article_list = db.relationship("Work_Article", backref="work_category", lazy="dynamic")


class Thinking_Categories(Base_Categories, db.Model):
    """定义宁静主题分类信息"""
    __tablename__ = "tb_thinking_category"
    thinking_article_list = db.relationship("Thinking_Article", backref="thinking_category", lazy="dynamic")


class Base_Comment(object):
    """定义评论基类"""
    id = db.Column(db.Integer, primary_key=True)
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("tb_user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 评论内容
    like_count = db.Column(db.Integer, default=0)  # 点赞计数
    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "content": self.content,
            "user": User.query.get(self.user_id).to_dict(),
            "like_count": self.like_count
        }

class Free_Comment(BaseModel, Base_Comment, db.Model):
    """定义自由主题的评论模型类"""
    __tablename__ = "tb_free_comment"
    free_article_id = db.Column(db.Integer, db.ForeignKey("tb_free_article.id"), nullable=False)
    free_parent_id = db.Column(db.Integer, db.ForeignKey("tb_free_comment.id"))  # 父评论id
    free_parent = db.relationship("Free_Comment", remote_side=[id])  # 自关联

    def to_dict(self):
        resp_dict = {
            "create_time": self.creat_time.strftime("%Y-%m-%d-%H:%M:%S"),
            "free_parent": self.free_parent.to_dict() if self.free_parent else None,
            "free_article_id": self.free_article_id
        }
        base_resp_dict = super().to_dict()
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict

class Work_Comment(BaseModel, Base_Comment, db.Model):
    """定义拼搏主题的评论模型类"""
    __tablename__ = "tb_work_comment"
    work_article_id = db.Column(db.Integer, db.ForeignKey("tb_work_article.id"), nullable=False)
    work_parent_id = db.Column(db.Integer, db.ForeignKey("tb_work_comment.id"))  # 父评论id
    work_parent = db.relationship("Work_Comment", remote_side=[id])  # 自关联

    def to_dict(self):
        resp_dict = {
            "create_time": self.creat_time.strftime("%Y-%m-%d-%H:%M:%S"),
            "work_parent": self.work_parent.to_dict() if self.work_parent else None,
            "work_article_id": self.work_article_id
        }
        base_resp_dict = super().to_dict()
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict

class Thinking_Comment(BaseModel, Base_Comment, db.Model):
    """定义宁静主题的评论模型类"""
    __tablename__ = "tb_thinking_comment"
    thinking_article_id = db.Column(db.Integer, db.ForeignKey("tb_thinking_article.id"), nullable=False)
    thinking_parent_id = db.Column(db.Integer, db.ForeignKey("tb_thinking_comment.id"))  # 父评论id
    thinking_parent = db.relationship("Thinking_Comment", remote_side=[id])  # 自关联

    def to_dict(self):
        resp_dict = {
            "create_time": self.creat_time.strftime("%Y-%m-%d-%H:%M:%S"),
            "thinking_parent": self.thinking_parent.to_dict() if self.thinking_parent else None,
            "thinking_article_id": self.thinking_article_id
        }
        base_resp_dict = super().to_dict()
        resp_dict = {**base_resp_dict, **resp_dict}
        return resp_dict



class Base_CommentLike(object):
    """定义点赞基类"""
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("tb_user.id"), primary_key=True)

class Free_Comment_like(BaseModel, Base_CommentLike, db.Model):
    """定义自由主题点赞模型类"""
    __tablename__ = "tb_free_comment_like"
    free_comment_id = db.Column(db.Integer, db.ForeignKey("tb_free_comment.id"), primary_key=True)

class Work_Comment_like(BaseModel, Base_CommentLike, db.Model):
    """定义拼搏主题点赞模型类"""
    __tablename__ = "tb_work_comment_like"
    work_comment_id = db.Column(db.Integer, db.ForeignKey("tb_work_comment.id"), primary_key=True)


class Thinking_Comment_like(BaseModel, Base_CommentLike, db.Model):
    """定义宁静主题点赞模型类"""
    __tablename__ = "tb_thinking_comment_like"
    thinking_comment_id = db.Column(db.Integer, db.ForeignKey("tb_thinking_comment.id"), primary_key=True)











# @login_manager.user_loader
# def user_loader(id):
#     return User.query.get(int(id))

