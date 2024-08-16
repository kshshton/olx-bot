import csv
import json
import webbrowser
import winsound
from tkinter.messagebox import askyesno

from playwright.sync_api import Playwright

from src.gui import GUI


class Bot:
    def __init__(self, filename) -> None:
        self.metadata = f"{filename}.json"
        self.spreadsheet = f"{filename}.csv"
        data_file = self.load_metadata_file()
        links = data_file.get("links")
        self.previous_links = set(links) if links else set()
        self.url = data_file.get("default_url")
        self.save = False
        self.alert = False
        if not self.url:
            input = GUI()
            self.url = input.url
            self.save = input.save
            self.alert = input.alert

    def make_sound(self) -> None:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def load_metadata_file(self) -> dict:
        try:
            with open(self.metadata, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_previous_values(self) -> None:
        with open(self.metadata, 'w') as file:
            json.dump({
                "links": list(self.previous_links),
                "default_url": self.url if self.save else None
            }, file)

    def open_links(self, current_links: set) -> None:
        new_links = current_links - self.previous_links
        if len(new_links) > 0:
            self.make_sound()
            message = (
                f"Liczba znalezionych linków: {
                    len(new_links)}\nCzy chcesz je otworzyć?"
            )
            if askyesno(message=message):
                for link in new_links:
                    webbrowser.open(link)

    def save_links_to_csv(self) -> None:
        with open(self.spreadsheet, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for link in self.load_metadata_file()["links"]:
                writer.writerow([link])

    def run(self, playwright: Playwright) -> None:
        firefox = playwright.firefox
        browser = firefox.launch()
        page = browser.new_page()
        page.goto(self.url)
        flats_from_page = page.evaluate(
            """
            Array.from(
                document.querySelector('div[data-testid="listing-grid"]')
                    .getElementsByTagName('a'))
                    .map(e => "https://www.olx.pl" + e.getAttribute('href')
            );
            """
        )
        current_links = set(flats_from_page)
        button = page.locator("[data-cy=pagination-forward]")

        while button.is_visible():
            button.click()
            page.wait_for_timeout(2000)
            flats_from_page = self._get_flats_from_page(page)
            current_links.update(flats_from_page)

        if current_links != self.previous_links and self.alert:
            self.open_links(current_links)

        self.previous_links = current_links
        self.save_previous_values()
        self.save_links_to_csv()
        browser.close()
