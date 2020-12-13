import re


def register(app):

    @app.template_filter()
    def mentions(text, usernames):
        """ convert @ mentions in text to links to user profiles
            Regex based on https://www.regextester.com/95875
        """
        mentions = re.findall('\s([@][\w_-]+)', text)
        valid_mentions = [m for m in mentions if m[1:] in usernames]

        for vm in valid_mentions:
            text = f'<a href="/user/{vm[1:]}">{vm}</a>'.join(text.split(vm))

        return text


        # split_text = re.split('(\W)', text)
        #
        # print(split_text, users)
        #
        # mention_found = False
        # for i, word in enumerate(split_text):
        #     if word == '@':
        #         mention_found = True
        #     else:
        #         if mention_found:
        #             if word in users:
        #                 split_text[i] = f'<a href="/user/{remainder}">{word}</a>'
        #             mention_found = False
        #     # if len(word) > 1 and word[0] == '@':
        #     #     print(word)
        #     #     remainder = word[1:]
        #     #     if remainder in users:
        #     #         split_text[i] = f'<a href="/user/{remainder}">{word}</a>'
        #
        # return ''.join(split_text)
