from app import app, db
from app.models import User, Post
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.flaskenv')
load_dotenv(dotenv_path)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
