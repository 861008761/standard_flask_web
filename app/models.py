#-*- acoding:utf-8 -*-
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from .exceptions import ValidationError

# 用户回调函数，返回用户对象或者None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#“关注”功能的中间表


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    image_url = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # 初始化用户并赋予权限，如果基类没有进行权限赋值，那么这里进行判断，如果邮箱地址和本地的FLASKY_MAIL_ADMIN相同，则赋值为管理员；否则默认赋值为普通用户

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_MAIL_ADMIN'] or self.email == "861008761@qq.com":
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None and self.image_url is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
            # self.image_url = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    def __repr__(self):
        return '<user %s>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成新的确认修改邮箱的邮件链接，把新的邮箱地址放到dumps中
    def generate_confirmationwithaddress_token(self, expiration=3600, address=None):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id, 'address': address})

    # 验证修改邮箱请求的正确性
    def confirm_address(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        address = data.get('address')
        if self.query.filter_by(email=address).first() is not None:
            return False
        self.email = address
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    # 检查用户是否具有某种权限
    def can(self, permissions):
        return self.role is not None and (permissions & self.role.permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    # 用户每次登录都刷新last_seen参数 最后访问时间

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # gravatar生成用户头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    # 生成随机用户
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # 关注者与被关注者数据库关系
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan'
                                )

    # 关注
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            return True
    # 取消关注

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    # 是否关注

    def is_following(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            return True
        else:
            return False
    # 是否被关注

    def is_followed_by(self, user):
        #f = user.followed.filter_by(followed_id = self.id).first()
        f = self.followers.filter_by(follower_id=user.id).first()
        if f:
            return True
        else:
            return False

    # 把用户设置为自己的关注者
    @staticmethod
    def add_self_follow():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    # 获取关注者关注对象的文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    # 生成认证
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    # 验证
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    # User转json格式 为了保护隐私，邮箱和角色没有放到json中
    def to_json(self):
        json_user = {
            'id': self.id,
            'email': self.email,
            'avatar_hash': self.avatar_hash,
            'image_url': self.image_url,
            'confirmed': self.confirmed,
            'permission': self.role.permissions,
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    # 用于生成用户头像url唯一标识，返回用户名username字段
    def getUserName(self):
        return self.username

    # 用于设置image_url属性
    def setImage_url(self, image_url):
        self.image_url = image_url

    def getImage_url(self):
        url = '%s' % self.image_url.split('app')[1]
        print url
        return url


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<role %s>' % self.name

    # 生成默认角色
    @staticmethod
    def insert_role():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text())
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # 把markdown文本转换成html文本

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p'
                        ]
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    # 生成json格式的posts
    # json中有一个虚构的属性
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'id': self.id,
            'author_name': self.author.username,
            'author_avatar_hash': self.author.avatar_hash,
            'author_image_url': self.author.image_url,
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    # json格式生成Post对象
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post doesn\'t have a body')
        return Post(body=body)

    # 生成随机博客
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        author=u
                        )
            db.session.add(post)
            db.session.commit()

# db数据库注册监听事件，一旦body改变，则执行 on_changed_body 方法
db.event.listen(Post.body, 'set', Post.on_changed_body)


# 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    body_html = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    # 生成json格式
    def to_json(self):
        json_comment = {
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'disabled': self.disabled,
            'author_username': self.author.username,
            'author': url_for('api.get_user', id=self.author_id),
            'post_id': self.post_id
        }
        return json_comment

    # json转Comment对象
    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body == '' or body is None:
            return ValidationError('body is empty')
        return Comment(body=body)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                        'em', 'i', 'strong'
                        ]
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser  # 好奇，不用加()的吗
