class NovelModel(object):

    def get_simple_info(self, name, href):
        return {'name': name, 'href': href}

    def get_chapter(self, name, href, content):
        return {
            'name': name,
            'href': href,
            'content': content
        }

    def get_novel_info(self, name, classify, cover, cover_width, cover_height, author, desc, chapters):
        return {
            'name': name,
            'classify': classify,
            'cover': cover,
            'cover_width': cover_width,
            'cover_height': cover_height,
            'author': author,
            'desc': desc,
            'chapters': chapters
        }
