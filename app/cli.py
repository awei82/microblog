from app.models import Post
import click


def register(app):
    @app.cli.group()
    def search():
        """Elasticsearch commands."""
        pass

    @search.command()
    def reindex():
        """Reindex Elasticsearch w/ posts from db."""
        Post.reindex()
