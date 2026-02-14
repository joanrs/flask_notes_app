from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Association table for many-to-many relationship between users and shared notes
note_sharing = db.Table('note_sharing',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('shared_at', db.DateTime, default=datetime.utcnow)
)

# Association table for user following relationships
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_at', db.DateTime, default=datetime.utcnow)
)

# Association table for user badges
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True)

    # Relationships
    notes = db.relationship('Note', backref='author', lazy=True, foreign_keys='Note.user_id')
    tasks = db.relationship('Task', backref='user', lazy=True)
    likes_given = db.relationship('Like', backref='user', lazy=True)
    
    # Notes shared WITH this user
    shared_with_me = db.relationship('Note', secondary=note_sharing, 
                                    backref=db.backref('shared_with', lazy='dynamic'), lazy='dynamic')
    
    # Following relationships
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    # Badges relationship
    badges = db.relationship('Badge', secondary=user_badges, 
                           backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    
    # Reputation system
    reputation_points = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.followed.count()
    
    def get_followed_notes(self):
        """Get notes from users this user follows"""
        followed_users = self.followed.all()
        followed_ids = [user.id for user in followed_users]
        followed_ids.append(self.id)  # Include own notes
        return Note.query.filter(Note.user_id.in_(followed_ids), Note.is_public == True).order_by(Note.created_at.desc())
    
    def get_likes_received(self):
        """Get total likes received on user's notes"""
        from sqlalchemy import func
        return db.session.query(func.count(Like.id)).join(Note).filter(Note.user_id == self.id).scalar() or 0
    
    def get_comments_made(self):
        """Get total comments made by user"""
        return Comment.query.filter_by(user_id=self.id).count()
    
    def calculate_reputation(self):
        """Calculate and update user reputation based on activity"""
        points = 0
        
        # Points for notes created
        points += len(self.notes) * 10
        
        # Points for likes received
        points += self.get_likes_received() * 5
        
        # Points for comments made
        points += self.get_comments_made() * 2
        
        # Points for followers
        points += self.get_followers_count() * 3
        
        # Points for being followed (social proof)
        points += self.get_following_count() * 1
        
        self.reputation_points = points
        return points
    
    def check_and_award_badges(self):
        """Check if user qualifies for new badges and award them"""
        from extensions import db
        
        # Get all badges user doesn't have yet
        current_badge_ids = [badge.id for badge in self.badges]
        available_badges = Badge.query.filter(~Badge.id.in_(current_badge_ids)).all()
        
        newly_awarded = []
        
        for badge in available_badges:
            earned = False
            
            if badge.requirement_type == 'notes_count':
                earned = len(self.notes) >= badge.requirement_value
            elif badge.requirement_type == 'likes_received':
                earned = self.get_likes_received() >= badge.requirement_value
            elif badge.requirement_type == 'comments_made':
                earned = self.get_comments_made() >= badge.requirement_value
            elif badge.requirement_type == 'followers_count':
                earned = self.get_followers_count() >= badge.requirement_value
            elif badge.requirement_type == 'reputation_points':
                earned = self.reputation_points >= badge.requirement_value
            
            if earned:
                self.badges.append(badge)
                newly_awarded.append(badge)
        
        if newly_awarded:
            db.session.commit()
        
        return newly_awarded
    
    def get_badges_list(self):
        """Get badges as a list for template usage"""
        return self.badges.all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'profile_pic': self.profile_pic,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'reputation_points': self.reputation_points,
            'followers_count': self.get_followers_count(),
            'following_count': self.get_following_count(),
            'notes_count': len(self.notes)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(20), default='#ffffff')
    icon = db.Column(db.String(50), default='fas fa-tag') # FontAwesome icon
    notes = db.relationship('Note', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    is_public = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    attachments = db.relationship('Attachment', backref='note', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='note', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='note', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def is_liked_by(self, user):
        """Check if note is liked by specific user"""
        return Like.query.filter_by(note_id=self.id, user_id=user.id).first() is not None
    
    def get_top_level_comments(self):
        """Get comments that are not replies"""
        return Comment.query.filter_by(note_id=self.id, parent_id=None).order_by(Comment.created_at.desc()).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_preview': self.content[:150] + ('...' if len(self.content) > 150 else ''),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_public': self.is_public,
            'view_count': self.view_count,
            'category_id': self.category_id,
            'category': {
                'id': self.category.id if self.category else None,
                'name': self.category.name if self.category else None,
                'color': self.category.color if self.category else None,
                'icon': self.category.icon if self.category else 'fas fa-tag'
            } if self.category else None,
            'attachments_count': len(self.attachments),
            'attachments': [{'id': a.id, 'filename': a.filename, 'file_type': a.file_type} for a in self.attachments],
            'likes_count': len(self.likes),
            'comments_count': len(self.comments),
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'profile_pic': self.author.profile_pic
            },
            'user_id': self.user_id
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, completed, overdue
    priority = db.Column(db.Integer, default=1) # 1: low, 2: medium, 3: high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('note_id', 'user_id', name='unique_note_user_like'),)
    
    def __repr__(self):
        return f'<Like for Note {self.note_id} by User {self.user_id}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # For replies
    
    # Relationships
    author = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'profile_pic': self.author.profile_pic
            },
            'replies_count': self.replies.count(),
            'is_reply': self.parent_id is not None
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on Note {self.note_id}>'

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fas fa-award')
    color = db.Column(db.String(20), default='#ffd700')
    requirement_type = db.Column(db.String(50), nullable=False)  # 'notes_count', 'likes_received', 'comments_made', etc.
    requirement_value = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Badge {self.name}>'
