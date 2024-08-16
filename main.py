import time

from playwright.sync_api import sync_playwright

from src.bot import Bot

WAIT_TIME: int = 1800


def main():
    bot = Bot(filename="mieszkania")

    while True:
        with sync_playwright() as playwright:
            bot.run(playwright)
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
