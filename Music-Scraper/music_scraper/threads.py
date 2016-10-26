import threading


class GUIThread(threading.Thread):
    """
    A thread used to run GUI in parallel

    :param CrawlerProcess process: Process of Scrapy that scrapes the Web for songs
    :param func: The function to run when the thread is started.
    """

    def __init__(self, process, func):
        threading.Thread.__init__(self)
        self.process = process
        self.func = func

    def run(self):
        self.func(self.process)


class DownloadThread(threading.Thread):
    """
    A thread used for downloading Audio files

    :param func: The function that is run in the thread.
    """

    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func

    def run(self):
        self.func()
