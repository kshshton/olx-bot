import json
import time
import webbrowser
import winsound
from tkinter.messagebox import askyesno

from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright

from gui import url_input

WAIT_TIME: int = 1800

load_dotenv()


class Bot:
    flat_links_script: str = """
        () => {
          return Array.from(
            document.querySelector('div[data-testid="listing-grid"]')
              .getElementsByTagName('a'))
              .map(e => "https://www.olx.pl" + e.getAttribute('href')
          );
        }
    """

    links_file_path: str = "links.json"

    def __init__(self) -> None:
        links_file = self.load_links_file()
        links = links_file.get("links")
        self.previous_links = links if links else set()
        self.url = links_file.get("default_url")
        self.save = False
        if not self.url:
            input = url_input()
            self.url = input["url"]
            self.save = input["save"]

    def make_sound(self) -> None:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def load_links_file(self) -> dict:
        try:
            with open(self.links_file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_previous_values(self) -> None:
        with open(self.links_file_path, 'w') as file:
            json.dump({
                "links": list(self.previous_links),
                "default_url": self.url if self.save else None
            }, file)

    def open_links(self, current_flat_links: set) -> None:
        new_links = current_flat_links - self.previous_links
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
        if current_flat_links != self.previous_links:
            self.open_links(current_flat_links)
        self.previous_links = current_flat_links
        self.save_previous_values()
        browser.close()


def main():
    bot = Bot()

    while True:
        with sync_playwright() as playwright:
            bot.run(playwright)
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
