import json
import time
import webbrowser
import winsound
from tkinter.messagebox import askyesno

import customtkinter as ctk
from playwright.sync_api import Playwright, sync_playwright

WAIT_TIME: int = 1800

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class GUI():
    def __init__(self) -> None:
        self.root = ctk.CTk()
        self.root.geometry("300x250")
        self.center_window(self.root)
        self.position = {"pady": 12, "padx": 10}
        self._url = ctk.StringVar(self.root)
        self._save = ctk.BooleanVar(self.root)
        self.create_widgets()

    @property
    def url(self):
        return self._url.get()

    @property
    def save(self):
        return self._save.get()

    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - window.winfo_reqwidth()) // 2
        y = (screen_height - window.winfo_reqheight()) // 2

        window.geometry(f"+{x}+{y}")

    def close(self, *args: any) -> None:
        self.root.destroy()

    def create_widgets(self):
        frame = ctk.CTkFrame(master=self.root)
        frame.pack(
            pady=20,
            padx=60,
            fill="both",
            expand=True,
        )

        label = ctk.CTkLabel(
            master=frame,
            text="Wklej URL:",
        )
        label.pack(**self.position)

        url_box = ctk.CTkEntry(
            master=frame,
            textvariable=self._url,
        )
        url_box.pack(**self.position)

        checkbox = ctk.CTkCheckBox(
            master=frame,
            text="Zapisz",
            variable=self._save,
        )
        checkbox.pack(**self.position)

        button = ctk.CTkButton(
            master=frame,
            text="Szukaj",
            command=self.close,
        )
        button.pack(**self.position)

        self.root.bind("<Return>", self.close)
        self.root.mainloop()


class Bot:
    flats_list: str = """
        () => {
          return Array.from(
            document.querySelector('div[data-testid="listing-grid"]')
              .getElementsByTagName('a'))
              .map(e => "https://www.olx.pl" + e.getAttribute('href')
          );
        }
    """

    data_file_name: str = "links.json"

    def __init__(self) -> None:
        data_file = self.load_links_file()
        links = data_file.get("links")
        self.previous_links = set(links) if links else set()
        self.url = data_file.get("default_url")
        self.save = False
        if not self.url:
            input = GUI()
            self.url = input.url
            self.save = input.save

    def make_sound(self) -> None:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def load_links_file(self) -> dict:
        try:
            with open(self.data_file_name, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_previous_values(self) -> None:
        with open(self.data_file_name, 'w') as file:
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

        flats_from_page = page.evaluate(self.flats_list)
        current_links = set(flats_from_page)
        button = page.locator("[data-cy=pagination-forward]")

        while button.is_visible():
            button.click()
            page.wait_for_timeout(2000)
            flats_from_page = page.evaluate(self.flats_list)
            current_links.update(flats_from_page)

        if current_links != self.previous_links:
            self.open_links(current_links)

        self.previous_links = current_links
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
