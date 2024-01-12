import json
import os
import time
import webbrowser
import winsound
from tkinter.messagebox import askyesno

from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright

URL: str = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/nowy-targ/?search%5Bfilter_enum_furniture%5D%5B0%5D=yes&search%5Bfilter_enum_rooms%5D%5B0%5D=four&search%5Bfilter_enum_rooms%5D%5B1%5D=three&search%5Bfilter_float_price%3Afrom%5D=1000&search%5Bfilter_float_price%3Ato%5D=2500"
WAIT_TIME: int = 1800

load_dotenv()


class Bot:
    flat_links_script: str = """
        () => {
          return Array.from(
            document.querySelectorAll('div[data-testid="listing-grid"]')
          )
            .flatMap(list => Array.from(list.getElementsByTagName('a'))
            .map(e => "https://www.olx.pl" + e.getAttribute('href')));
        }
    """

    previous_values_file: str = "previous_values.json"

    def __init__(self, url: str) -> None:
        self.url = url
        self.previous_flat_links = self.load_previous_values()

    def make_sound(self) -> None:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def load_previous_values(self) -> set:
        try:
            with open(self.previous_values_file, 'r') as file:
                return set(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def save_previous_values(self) -> None:
        with open(self.previous_values_file, 'w') as file:
            json.dump(list(self.previous_flat_links), file)

    def open_links(self, current_flat_links: set) -> None:
        new_links = current_flat_links - self.previous_flat_links
        if len(new_links) > 0:
            self.make_sound()
            message = "Czy chcesz otworzyć nowy link?" if len(
                new_links) == 1 else f"Czy chcesz otworzyć {len(new_links)} nowych linków?"
            if askyesno(message=message):
                for link in new_links:
                    webbrowser.open(link)

    def run(self, playwright: Playwright) -> None:
        firefox = playwright.firefox
        browser = firefox.launch()
        page = browser.new_page()
        page.goto(self.url)
        current_flat_links = set(page.evaluate(
            self.flat_links_script
        ))
        if current_flat_links != self.previous_flat_links:
            self.open_links(current_flat_links)
        self.previous_flat_links = current_flat_links
        self.save_previous_values()
        browser.close()


def main():
    bot = Bot(URL)

    while True:
        with sync_playwright() as playwright:
            bot.run(playwright)
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
