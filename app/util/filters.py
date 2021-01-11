import re


def register(app):

    @app.template_filter()
    def mentions(text, usernames):
        """ convert @ mentions in text to links to user profiles
            Regex based on https://www.regextester.com/95875
        """
        mentions = [x[1] for x in re.findall('(^|\s)([@][\w_-]+)', text)]
        valid_mentions = [m for m in mentions if m[1:] in usernames]

        for vm in valid_mentions:
            text = f'<a href="/user/{vm[1:]}">{vm}</a>'.join(text.split(vm))

        return text
