import json
import webbrowser
import winsound
from tkinter.messagebox import askyesno

from playwright.sync_api import Playwright

from src.gui import GUI


class Bot:
    def __init__(self, filename) -> None:
        self.filename = f"{filename}.json"
        data_file = self.load_links_file()
        links = data_file.get("links")
        self.previous_links = set(links) if links else set()
        self.url = data_file.get("default_url")
        self.save = False
        if not self.url:
            input = GUI()
            self.url = input.url
            self.save = input.save

    def _get_flats_from_page(page):
        return page.evaluate(
            """
            () => {
            return Array.from(
                document.querySelector('div[data-testid="listing-grid"]')
                .getElementsByTagName('a'))
                .map(e => "https://www.olx.pl" + e.getAttribute('href')
            );
            }
            """
        )

    def make_sound(self) -> None:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def load_links_file(self) -> dict:
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_previous_values(self) -> None:
        with open(self.filename, 'w') as file:
            json.dump({
                "links": list(self.previous_links),
                "default_url": self.url if self.save else None
            }, file)

    def open_links(self, current_links: set) -> None:
        new_links = current_links - self.previous_links
        if len(new_links) > 0:
            self.make_sound()
            message = (
                "Czy chcesz otworzyć nowy link?"
                if len(new_links) == 1
                else f"Czy chcesz otworzyć {len(new_links)} nowych linków?"
            )
            if askyesno(message=message):
                for link in new_links:
                    webbrowser.open(link)

    def run(self, playwright: Playwright) -> None:
        firefox = playwright.firefox
        browser = firefox.launch()
        page = browser.new_page()
        page.goto(self.url)

        flats_from_page = self._get_flats_from_page(page)
        current_links = set(flats_from_page)
        button = page.locator("[data-cy=pagination-forward]")

        while button.is_visible():
            button.click()
            page.wait_for_timeout(2000)
            flats_from_page = self._get_flats_from_page(page)
            current_links.update(flats_from_page)

        if current_links != self.previous_links:
            self.open_links(current_links)

        self.previous_links = current_links
        self.save_previous_values()
        browser.close()
