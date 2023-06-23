from flask import Flask, request, jsonify
from sqlalchemy import func
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime

from models.extensions import db
from models.user import User
from models.post import Post, Like


app = Flask(__name__)
app.config.from_object("config.Config")
db.init_app(app)
jwt = JWTManager(app)


def get_current_user_id():
    return int(get_jwt_identity()) if get_jwt_identity() else None


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username existed.'}), 401

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully.'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'error': 'Invalid username or password.'}), 401

    user.last_login = datetime.now()
    user.last_request = datetime.now()
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token})


@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Post content is required.'}), 400

    current_user_id = get_current_user_id()
    if not current_user_id:
        return jsonify({'error': 'User not found.'}), 404

    user = User.query.filter_by(id=current_user_id).first()
    user.last_request = datetime.now()

    created_at = datetime.now()
    post = Post(user_id=current_user_id, content=content, created_at=created_at)
    db.session.add(post)
    db.session.commit()
    return jsonify({
        'id': Post.query.filter_by(created_at=created_at).first().id,
        'message': 'Post created successfully.'
    })


@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_current_user_id()
    if not current_user_id:
        return jsonify({'error': 'User not found.'}), 404

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found.'}), 404

    if post.likes.filter_by(user_id=current_user_id).first():
        return jsonify({'error': 'You have already liked this post.'}), 400

    user = User.query.filter_by(id=current_user_id).first()
    user.last_request = datetime.now()

    post.likes.append(Like(user_id=current_user_id))
    db.session.commit()
    return jsonify({'message': 'Post liked successfully.'})


@app.route('/api/posts/<int:post_id>/unlike', methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    current_user_id = get_current_user_id()
    if not current_user_id:
        return jsonify({'error': 'User not found.'}), 404

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found.'}), 404

    like = post.likes.filter_by(user_id=current_user_id).first()
    if not like:
        return jsonify({'error': 'You have not liked this post.'}), 400

    user = User.query.filter_by(id=current_user_id).first()
    user.last_request = datetime.now()

    db.session.delete(like)
    db.session.commit()
    return jsonify({'message': 'Post unliked successfully.'})


@app.route('/api/analytics/', methods=['GET'])
@jwt_required()
def analytics():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    if not date_from or not date_to:
        return jsonify({'error': 'date_from and date_to parameters are required.'}), 400

    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    likes_count = db.session.query(
        func.date(Like.created_at).label('date'),
        func.count(Like.id).label('likes_count')
    ).filter(
        Like.created_at >= date_from,
        Like.created_at <= date_to
    ).group_by(
        func.date(Like.created_at)
    ).all()

    analytics_data = [{'date': date, 'likes_count': count} for date, count in likes_count]

    return jsonify({'analytics': analytics_data})


@app.route('/api/user/activity', methods=['GET'])
@jwt_required()
def user_activity():
    current_user_id = get_current_user_id()
    if not current_user_id:
        return jsonify({'error': 'User not found.'}), 404

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    return jsonify({
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'last_request': user.last_request.isoformat() if user.last_request else None
    })
