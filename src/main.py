import sideParser

if __name__ == '__main__':
    pass

side_event = sideParser.SideParser()
side_event.ignoreRobots()
side_event.openBrowser('http://www.example.fora.pl/login.php')
side_event.selectForm("action","login.php")
side_event.logUser()
side_event.createLinkMap()
side_event.createPostsMap()
side_event.logOut()
