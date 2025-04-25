import aiohttp
import asyncio

search_headers = {
    "Host": "www.kleinanzeigen.de",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i"
}

search_url = "https://www.kleinanzeigen.de/s-suchanfrage.html?keywords=calvin%20klein&categoryId=&locationStr=Berlin&radius=50&sortingField=SORTING_DATE&adType=&posterType=&pageNum=1&action=find&maxPrice=500&minPrice=5&buyNowEnabled=false&shippingCarrier="
item_url = "https://www.kleinanzeigen.de/s-anzeige/dji-osmo-action-5-pro-adventure-combo-ungeoeffnet/3047577797-245-3473"

async def fetch_and_store_cookies():
    async with aiohttp.ClientSession() as session:
        print("\n📄 Fetching items...")

        async with session.get(search_url, headers=search_headers) as response:
            print(f"Status: {response.status}")
            html = await response.text()
            # Save HTML to file
            with open("html_files/search_results.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Length of response: {len(html)} characters")

            # Печать всех cookies
            print("\n🍪 Cookies saved in session:")
            for cookie in session.cookie_jar:
                print(f"{cookie.key} = {cookie.value}")

        # Fetch individual item page using the same session
        print("\n📄 Fetching item page...")
        async with session.get(item_url, headers=search_headers) as item_response:
            print(f"Item page status: {item_response.status}")
            item_html = await item_response.text()
            
            # Save item HTML to file
            with open("html_files/item_result.html", "w", encoding="utf-8") as f:
                f.write(item_html)
            print(f"Item page saved: {len(item_html)} characters")
            
            # Print cookies after item request
            print("\n🍪 Cookies after item request:")
            for cookie in session.cookie_jar:
                print(f"{cookie.key} = {cookie.value}")



asyncio.run(fetch_and_store_cookies())
