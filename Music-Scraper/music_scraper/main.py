import curses

try:
    from urllib import request
except ImportError:
    import urllib2 as request

from scrapy.crawler import CrawlerProcess

from music_scraper.gui import GUI
from music_scraper.threads import GUIThread
from music_scraper.spiders.music_spider import MusicSpider

try:
    input = raw_input
except NameError:
    pass


def start_gui(process):
    """
    A function that takes care of starting the GUI and stops the Scrapy crawler process when exited from program.

    :param CrawlerProcess process: The scrapy crawler process that is used to scrape the web. The instance is used for stopping the process.
    """

    def create_ui(screen):
        """
        A function passes to curses wrapper for safe execution of terminal GUI.

        :param screen: The screen parameter to run the GUI. Sent from the curses wrapper.
        """

        GUI.screen = screen  # All the statis variables of the GUI class is initialized
        GUI.strings = []  # the list of songs is empty initially
        GUI.init_display()  # init the variables required for GUI
        GUI.update_on_key()  # Starts a loop that waits for key input and acts accordingly

        curses.nocbreak()
        curses.echo()
        curses.endwin()
        GUI.gui_stopped = True

    curses.wrapper(create_ui)
    process.stop()  # Stopping the scrapy crawler process


def main():
    """
    The entry point for the app. Called when music-scraper is typed in terminal.
    Starts the GUI and starts the scraping process after the input is given
    """
    curses.initscr()
    if curses.COLS < 80 or curses.LINES < 5:
        curses.endwin()
        print('Terminal\'s dimensions are too small')
        return

    process = CrawlerProcess({'LOG_ENABLED': False})

    def gui_input(screen):
        GUI.screen = screen
        curses.start_color()
        GUI.screen.keypad(1)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        GUI.high_light_text = curses.color_pair(1)
        GUI.normal_text = curses.A_NORMAL
        GUI.box = curses.newwin(curses.LINES, curses.COLS, 0, 0)
        GUI.message = GUI.get_input()

    curses.wrapper(gui_input)
    s = request.quote(GUI.message)

    MusicSpider.start_urls = [
        "http://www.google.com/search?q=" + s,
    ]
    process.crawl(MusicSpider)
    thread = GUIThread(process, start_gui)
    thread.start()
    process.start()
    if not GUI.gui_stopped:
        if len(GUI.strings) == 0:
            GUI.box.erase()
            GUI.box.addstr(1, 1, "No Results Found... Try with Some other keywords.", GUI.high_light_text)
            GUI.add_bottom_menus()
            GUI.screen.refresh()
            GUI.box.refresh()
        else:
            GUI.box.addstr(curses.LINES - 2, 1, "Completed Scraping !!", GUI.high_light_text)
            GUI.add_bottom_menus()
            GUI.screen.refresh()
            GUI.box.refresh()