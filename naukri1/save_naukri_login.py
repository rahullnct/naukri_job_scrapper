import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


AUTH_FILE = Path("naukri_auth.json").resolve()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
        )

        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(
            "https://www.naukri.com/",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print("\nNaukri browser opened.")
        print("Log in manually using your email, password and OTP.")
        print("After the Naukri home page shows that you are logged in,")

        await asyncio.to_thread(
            input,
            "press Enter in this terminal to save the login: ",
        )

        await context.storage_state(
            path=str(AUTH_FILE),
            indexed_db=True,
        )

        print(f"\nLogin saved successfully: {AUTH_FILE}")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
