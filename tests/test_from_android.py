import asyncio
import aiohttp
import random
import json

# Заголовки, имитирующие мобильное приложение
HEADERS = {
    "User-Agent": "Kleinanzeigen/100.43.3 (Android 9; google G011A)",
    "X-ECG-USER-AGENT": "ebayk-android-app-100.43.3",
    "X-ECG-USER-VERSION": "100.43.3",
    "X-EBAYK-APP": "b760cd24-4c2a-4cb8-9386-dff025040d6f1745598430588",
    "Authorization": "Basic YW5kcm9pZDpUYVI2MHBFdHRZ"
}

SEARCH_URL = "https://api.kleinanzeigen.de/api/ads.json"
DETAIL_URL = "https://api.kleinanzeigen.de/api/ads/{ad_id}.json"

# Параметры поиска
async def fetch_ads(session, query="tom ford", page=0, size=10):
    params = {
        "_in": "id,title,description,displayoptions,start-date-time,category.id,category.localized_name,"
               "ad-address.state,ad-address.zip-code,ad-address.availability-radius-in-km,price,pictures,"
               "link,features-active,search-distance,negotiation-enabled,attributes,medias,medias.media,"
               "medias.media.title,medias.media.media-link,buy-now,placeholder-image-present,labels,"
               "price-reduction,store-id,store-title",
        "q": query,
        "page": str(page),
        "size": str(size),
        "pictureRequired": "false",
        "includeTopAds": "true",
        "buyNowOnly": "false",
        "labelsGenerationEnabled": "true",
        "limitTotalResultCount": "true",
        "sortType": "DATE_DESCENDING"
    }
    async with session.get(SEARCH_URL, headers=HEADERS, params=params) as response:
        return await response.json()

# Получение деталей по ID
async def fetch_ad_details(session, ad_id):
    url = DETAIL_URL.format(ad_id=ad_id)
    async with session.get(url, headers=HEADERS) as response:
        return await response.json()

# Основная логика
async def main():
    async with aiohttp.ClientSession() as session:
        search_data = await fetch_ads(session, query="rayban meta")

        ads = search_data.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads", {}).get("value", {}).get("ad", [])
        print(f"Found {len(ads)} ads.")

        # Save search results to a JSON file
        output_file = "tests/api_item_list.json"
        
        # Convert the data to a more readable format if needed
        # In this case, we're just saving the raw response
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ads, f, ensure_ascii=False, indent=2)
        
        print(f"Search results saved to {output_file}")

        # selected_ads = random.sample(ads, min(4, len(ads)))
        # for ad in selected_ads:
        #     ad_id = ad.get("id")
        #     if ad_id:
        #         print(f"\nFetching details for ad ID: {ad_id}")
        #         detail = await fetch_ad_details(session, ad_id=ad_id)
        #         print(json.dumps(detail, indent=2)[:1000], "...")  # show only first 1000 chars

asyncio.run(main())
