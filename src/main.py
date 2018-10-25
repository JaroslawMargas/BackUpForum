import sideParser

if __name__ == '__main__':
    pass

side_event = sideParser.SideParser()
side_event.ignore_robots()
side_event.open_browser('http://www.EXAMPLE.fora.pl/login.php')
side_event.selectForm("action","login.php")
side_event.log_user()
side_event.createLinkMap('index.txt','class','topictitle')
side_event.createPostsMap('index.txt')
side_event.logOut()
