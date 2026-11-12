import asyncio
import json
import logging

from playwright.async_api import async_playwright


log = logging.getLogger(__name__)

async def main(payload):
    try:
        #STEP 1: Launch a headless chromium browser
        data = json.loads(payload.decode('utf-8'))
        url = data["destination"]
        log.info(f"Extracted the url target: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page=await browser.new_page()

            #STEP 2: Navigate to the targeted pagination URL
            url = url
            log.info(f"Navigating to url: {url}")

            await page.goto(url)

            #STEP 3: Wait for the items to load completely in the DOM
            #To guide us, wait for the H3 element in the containers

            await page.wait_for_selector("h3")

            #STEP 4: Find all item container blocks on the page
            items_data=[]

            product_headers = await page.query_selector_all("h3")
            log.info(f"Found {len(product_headers)} product headers")

            for header in product_headers:
                #Extract the headers for each product
                title = await header.inner_text()

                #Go to the parent element
                parent_card = await header.evaluate_handle("element => element.parentElement")
                
                description_element = await parent_card.query_selector("p.description")
                description = await description_element.inner_text() if description_element else ""
                
                card_text = await parent_card.inner_text()
                next_lines = await parent_card.evaluate("el => el.nextElementSibling ? el.nextElementSibling.innerText : ''")
               

                #Go through each line the the 
                lines =[line.strip() for line in card_text.split('\n') if line.strip()]
                price = "N/A"
                year = "N/A"
                country = "N/A"
                mileage = "N/A"

                for line in lines:
                    log.info(f"Line: {line}")
                    if "Year" in line:
                        year=line.replace("Year","").strip()
                    elif "Country of origin" in line:
                        country = line.replace ("Country of origin:", "").strip()
                    elif "Mileage" in line:
                        mileage=line.replace("Mileage:","").strip()

                    elif "USD" in line:
                        price=line

                for next_line in next_lines.split("\n"):
                    log.info(f"Next line content: {next_line}")
                    if "USD" in next_line:
                        price = next_line.strip()
        
                items_data.append({
                    "title": title,
                    "price": price,
                    "year": year,
                    "country_of_origin": country,
                    "mileage": mileage
                })

                #STEP 5: Save the collected data into a structure JSON file
                output_file = "scraped_products.json"

                with open(output_file,"w", encoding="utf-8") as f:
                    json.dump(items_data, f, indent=4, ensure_ascii=False)

        log.info("Successfully scraped the data")
        return items_data
            
    except Exception as e:
        log.error(f"Experienced an error: {e} scraping url: {url}")

    await browser.close()

            

        