import asyncio
import json
import logging

from playwright.async_api import async_playwright

from app.rag.langchain_rag import LangchainRAG


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

            # STEP 3: Wait for the initial items to load
            await page.wait_for_selector("h3")

            # --- INFINITE SCROLL LOGIC ---
            last_height = await page.evaluate("document.body.scrollHeight")

            while True:
                # Scroll to the bottom of the page
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load (adjust timeout/delay based on network speed)
                try:
                    await page.wait_for_timeout(2000) # Wait 2 seconds for new elements to render
                except Exception:
                    pass
                
                # Calculate new scroll height and compare with last height
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    log.info("Reached the bottom of the page. No more items to load.")
                    break
                
                last_height = new_height
            # -----------------------------

            # STEP 4: Find all item container blocks on the page after full scroll
            items_data = []

            product_headers = await page.query_selector_all("h3")
            log.info(f"Found {len(product_headers)} total product headers")

            for header in product_headers:
                # Extract the headers for each product
                title = await header.inner_text()

                # Go to the parent element
                parent_card = await header.evaluate_handle("element => element.parentElement")
                
                description_element = await parent_card.query_selector("p.description")
                description = await description_element.inner_text() if description_element else ""
                
                card_text = await parent_card.inner_text()
                next_lines = await parent_card.evaluate("el => el.nextElementSibling ? el.nextElementSibling.innerText : ''")
    
    # (Optional) Append to items_data here...
               

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

        #Now storing them in chroma db for retrieval
        log.info("Creating data embeddings ...")
        rag = LangchainRAG()

        rag.create_embeds()
        return items_data
            
    except Exception as e:
        log.error(f"Experienced an error: {e} scraping url: {url}")

    await browser.close()

            

        