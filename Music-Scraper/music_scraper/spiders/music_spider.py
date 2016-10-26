import cgi

import scrapy

from music_scraper.gui import GUI

items = []


def is_standard_website(href):
    """
    Function to remove urls belonging to some famous sites

    :param str href: the url
    :return bool: True or False
    """
    if 'google' not in href and 'youtube' not in href and 'twitter' not in href and 'facebook' not in href:
        return True
    else:
        return False


class MusicSpider(scrapy.Spider):

    # Name of the spider
    name = "music"

    def parse(self, response):
        """
        Override function of the class scrapy.Spider. Called when response is obtained
        :param response: Response object used to get the details of the webpage
        """
        for href in response.xpath("//a/@href").extract():
            # Iterating over all the urls in the google search page
            if href[:7] == '/url?q=' and is_standard_website(href):
                # Getting the search results alone
                url = href[7:].split('&')[0]
                # starting another request for each search result url
                yield scrapy.Request(url, meta={'download_maxsize': 2097152}, callback=self.parse_result_contents)

    def parse_result_contents(self, response):
        """
        Callback function called when the webpage of each result is opened.
        :param response: Response object used to get the details of the webpage
        """
        for sel in response.xpath('//a/@href').extract():
            # Iterating over all the urls in each of the result.
            url = response.urljoin(sel)
            # Check whether each url is an audio file by its header
            yield scrapy.Request(url, method='HEAD', callback=self.parse_header)

    def parse_header(self, response):
        """
        Callback function called when header of each link in each result is obtained
        :param response: Response object used to get the details of the webpage
        """
        # Check if header is audio/mpeg
        if response.headers['Content-Type'].decode('UTF-8') == 'audio/mpeg':
            # Get the file name
            _, params = cgi.parse_header(response.headers.get('Content-Disposition', '').decode('UTF-8'))
            filename = params['filename']
            # Loop to remove redundant names
            while True:
                if GUI.url_dict.get(filename) is None:
                    GUI.url_dict[filename] = response.url
                    GUI.size_dict[filename] = int(response.headers['Content-Length'].decode('UTF-8'))
                    break
                else:
                    split_file = filename.split('.')
                    filename = '.'.join(split_file[:-1]) + '_.' + split_file[-1]
            # Add file names to the list to be displayed in GUI
            GUI.strings += [filename]
            GUI.refresh_values()
            GUI.update_screen()
