from flask import render_template, flash, redirect, url_for, request, g, current_app, jsonify
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, MessageForm, EditPostForm
from app.main import bp
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Message, Notification

from datetime import datetime
import os
from werkzeug.utils import secure_filename


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!')
            return redirect(url_for('main.index'))

        page = request.args.get('page', 1, type=int)
        posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
        usernames = db.session.query(User.username).all()
        usernames = [x[0] for x in usernames]
        return render_template('home.html', title='Home', form=form,
                               posts=posts.items, next_url=next_url,
                               prev_url=prev_url, usernames=usernames)
    else:
        return render_template('index.html', title='Welcome')


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    usernames = db.session.query(User.username).all()
    usernames = [x[0] for x in usernames]
    return render_template("home.html", title='Explore',
                           posts=posts.items, next_url=next_url, prev_url=prev_url, usernames=usernames)


@bp.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=users.next_num) if users.has_next else None
    prev_url = url_for('main.explore', page=users.prev_num) if users.has_prev else None
    form = EmptyForm()
    return render_template("users.html", title='Users',
                           users=users.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    usernames = db.session.query(User.username).all()
    usernames = [x[0] for x in usernames]
    return render_template('user.html', title=user.username,
                           user=user, posts=posts.items, next_url=next_url, prev_url=prev_url,
                           form=form, usernames=usernames)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        # save profile photo
        if form.profile_photo.data:
            image_data = request.files[form.profile_photo.name]
            image_data.save(os.path.join('app/static', 'profile_photos', str(current_user.id) + '.jpg'))

        flash('Your changes have been saved. Profile photo changes may take a moment to load.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(request.referrer)
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(request.referrer)
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(request.referrer)
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(request.referrer)
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title='Send Message', form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', title='Messages',
                           messages=messages.items, next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{'name': n.name,
                     'data': n.get_data(),
                     'timestamp': n.timestamp
                     } for n in notifications])


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash('An export task is currently in progress')
    else:
        flash('Export task started.')
        current_user.launch_task('export_posts', 'Exporting posts...')
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/post/<id>')
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    usernames = db.session.query(User.username).all()
    usernames = [x[0] for x in usernames]
    return render_template('post.html', title=f'Post: {id}',
                           post=post, form=form, author=post.author.username, usernames=usernames)


@bp.route('/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first_or_404()

    form = EditPostForm()

    if form.validate_on_submit():
        if form.submit.data:
            post.body = form.post.data
            post.updated_timestamp = datetime.utcnow()
            db.session.commit()
            flash('Your post has been updated.')
            return redirect(url_for('main.post', id=id))
        elif form.delete.data:
            db.session.delete(post)
            db.session.commit()
            flash('Your post has been deleted.')
            return redirect(url_for('main.index'))

    elif request.method == 'GET':
        form.post.data = post.body
        usernames = db.session.query(User.username).all()
        usernames = [x[0] for x in usernames]
    return render_template('edit_post.html', title=f'Edit Post: {id}',
                           post=post, form=form, author=post.author.username, usernames=usernames)