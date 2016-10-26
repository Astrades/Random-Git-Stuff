import curses
try:
    from urllib import request
except ImportError:
    import urllib2 as request

from math import ceil

from music_scraper.threads import DownloadThread


class GUI:
    """
    A static class containing attributes to control the GUI process of the app

    Attributes:
        :screen: The maximum speed that such a bird can attain.
        :status: The locale where these birds congregate to reproduce.
        :strings: The list of song names, scraped from the web
        :size_dict: Dictionary mapping file names to size of file.
        :url_dict: Dictionary mapping file names to url of file.
        :pages: Total number of pages required to display the song list.
        :page: current page number
        :position: current highlighted song name.
        :max_row: Maximum number of rows that can be displayed in the terminal window.
        :row_num: Total number of rows required.
        :box: Box object which is drawn on the screen with curses
        :high_light_text: curses color of highlighted text.
        :normal_text: Normal text color.
        :key: current pressed key value.
        :run_download: Used to indicate an ongoing download
        :gui_stopped: Used to indicate whether GUI is on or off
        :message: The message or query passed to scrapy and got as input from user
    """

    screen = None
    status = 'Scraping Music ... It might take some time.'

    # Song links' info
    strings = []
    size_dict = {}
    url_dict = {}

    # Info used to diaplay list
    pages = 0
    page = 1
    position = 1
    max_row = 0
    row_num = 0
    box = None
    high_light_text = None
    normal_text = None
    key = None
    run_download = False    # Used to indicate an ongoing download
    gui_stopped = False     # Used to indicate whether GUI is on or off
    message = ''            # The message or query passed to scrapy and got as input from user

    @staticmethod
    def init_display():
        """
        Inits the display GUI
        """
        if not GUI.gui_stopped:
            curses.noecho()
            curses.cbreak()
            curses.start_color()
            GUI.screen.keypad(1)
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
            GUI.high_light_text = curses.color_pair(1)
            GUI.normal_text = curses.A_NORMAL
            curses.curs_set(0)
            GUI.refresh_values()
            GUI.position = 1
            GUI.page = 1
            GUI.box = curses.newwin(GUI.max_row + 3, curses.COLS, 0, 0)
            GUI.box.addstr(1, 1, GUI.status, GUI.high_light_text)
            GUI.add_bottom_menus()
            GUI.screen.refresh()
            GUI.box.refresh()

    @staticmethod
    def refresh_values():
        """
        Refresh the parameters when the size of list changes in display
        """
        if not GUI.gui_stopped:
            GUI.max_row = curses.LINES - 3
            GUI.row_num = len(GUI.strings)
            GUI.pages = int(ceil(GUI.row_num / GUI.max_row))

    @staticmethod
    def add_bottom_menus():
        """
        Adds the bottom menu Exit and Download
        """
        GUI.box.addstr(curses.LINES - 1, 0, "ESC:Exit", GUI.high_light_text)
        GUI.box.addstr(curses.LINES - 1, curses.COLS // 2, "ENTR:Download", GUI.high_light_text)

    @staticmethod
    def on_key_down():
        """
        Called when down arrow is pressed
        """
        if GUI.page == 1:
            if GUI.position < min(GUI.max_row, GUI.row_num):
                GUI.position += 1
            else:
                if GUI.pages > 1:
                    GUI.page += 1
                    GUI.position = 1 + (GUI.max_row * (GUI.page - 1))
        elif GUI.page == GUI.pages:
            if GUI.position < GUI.row_num:
                GUI.position += 1
        else:
            if GUI.position < GUI.max_row + (GUI.max_row * (GUI.page - 1)):
                GUI.position += 1
            else:
                GUI.page += 1
                GUI.position = 1 + (GUI.max_row * (GUI.page - 1))

    @staticmethod
    def on_key_up():
        """
        Called when up arrow key is pressed.
        """
        if GUI.page == 1:
            if GUI.position > 1:
                GUI.position -= 1
        else:
            if GUI.position > (1 + (GUI.max_row * (GUI.page - 1))):
                GUI.position -= 1
            else:
                GUI.page -= 1
                GUI.position = GUI.max_row + (GUI.max_row * (GUI.page - 1))

    @staticmethod
    def on_key_left():
        """
        Called when left arrow key is pressed.
        """
        if GUI.page > 1:
            GUI.page -= 1
            GUI.position = 1 + (GUI.max_row * (GUI.page - 1))

    @staticmethod
    def on_key_right():
        """
        Called when right arrow key is pressed.
        """
        if GUI.page < GUI.pages:
            GUI.page += 1
            GUI.position = (1 + (GUI.max_row * (GUI.page - 1)))

    @staticmethod
    def on_key_enter():
        """
        Called when enter key is pressed. It starts the download process in a new thread
        """
        thread = DownloadThread(GUI.download_item)
        thread.start()

    @staticmethod
    def display_list():
        """
        Displays the list of song names scraped from web.
        """
        for i in range(1 + (GUI.max_row * (GUI.page - 1)), GUI.max_row + 1 + (GUI.max_row * (GUI.page - 1))):
            if GUI.row_num == 0:
                GUI.box.addstr(1, 1, GUI.status, GUI.high_light_text)
            else:
                if i + (GUI.max_row * (GUI.page - 1)) == GUI.position + (GUI.max_row * (GUI.page - 1)):
                    GUI.box.addstr(i - (GUI.max_row * (GUI.page - 1)), 2, (str(i) + " - " + GUI.strings[i - 1] +
                                   " : %.2fMB") % (GUI.size_dict[GUI.strings[i - 1]]/1024/1024), GUI.high_light_text)
                else:
                    GUI.box.addstr(i - (GUI.max_row * (GUI.page - 1)), 2, (str(i) + " - " + GUI.strings[i - 1] +
                                   " : %.2fMB") % (GUI.size_dict[GUI.strings[i - 1]]/1024/1024), GUI.normal_text)
                if i == GUI.row_num:
                    break

    @staticmethod
    def update_screen():
        """
        Updates the screen each time a key is pressed.
        """
        if not GUI.gui_stopped:
            if GUI.key == curses.KEY_DOWN:
                GUI.on_key_down()
            elif GUI.key == curses.KEY_UP:
                GUI.on_key_up()
            elif GUI.key == curses.KEY_LEFT:
                GUI.on_key_left()
            elif GUI.key == curses.KEY_RIGHT:
                GUI.on_key_right()
            if GUI.key == ord("\n") and GUI.row_num != 0:
                GUI.on_key_enter()

            GUI.box.erase()
            GUI.display_list()
            GUI.add_bottom_menus()
            GUI.screen.refresh()
            GUI.box.refresh()

    @staticmethod
    def update_on_key():
        """
        Loops to get a key input and updates the screen accordingly
        """
        if not GUI.gui_stopped:
            GUI.key = GUI.screen.getch()
            while GUI.key != 27 or GUI.run_download:
                if ord('c') == GUI.key or ord('C') == GUI.key:
                    GUI.run_download = False
                GUI.update_screen()
                GUI.key = GUI.screen.getch()
            curses.endwin()

    @staticmethod
    def download_item():
        """
        It downloads the song from the url and saves it in the file.
        """
        if GUI.run_download or GUI.gui_stopped:
            return
        GUI.run_download = True
        filename = GUI.strings[GUI.position - 1]
        url = GUI.url_dict[filename]
        # User agent is specified to prevent some websites from blocking the software
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        u = request.urlopen(req)
        f = open(filename, 'wb')

        file_size_dl = 0
        block_sz = 8192
        while GUI.run_download:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            # The percentage downloaded
            status = "Downloading " + filename + " [%3.2f%%]" % (file_size_dl * 100. / GUI.size_dict[filename])
            GUI.box.erase()
            GUI.box.addstr(1, 1, status, GUI.high_light_text)
            GUI.box.addstr(2, 1, 'Size: %.2fMB' % (GUI.size_dict[filename]/1024/1024))
            # Cancel button to cancel the download
            GUI.box.addstr(curses.LINES - 1, 0, "C:Cancel Download", GUI.high_light_text)
            GUI.screen.refresh()
            GUI.box.refresh()

        f.close()
        GUI.run_download = False
        GUI.key = curses.KEY_DOWN
        GUI.update_screen()

    @staticmethod
    def my_raw_input(r, c, prompt_string):
        """
        Gets input on the screen
        :param r: y coordinate
        :param c: x coordinate
        :param prompt_string: The prompt string
        :return: The input string
        """
        curses.echo()
        GUI.box.addstr(r, c, prompt_string, GUI.high_light_text)
        GUI.box.refresh()
        input_str = GUI.box.getstr(r + 2, c, curses.COLS)
        return input_str.decode('UTF-8')

    @staticmethod
    def get_input():
        """
        Loops till user types a non empty query
        :return: The user inputted query.
        """
        input_str = ''
        while input_str == '':
            input_str = GUI.my_raw_input(1, 1, 'Give me something to start with - (Example: kabali song download):')
        return input_str
