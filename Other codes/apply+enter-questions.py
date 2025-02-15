import asyncio
from playwright.async_api import async_playwright
import time

from openai import OpenAI


import openai
from dotenv import load_dotenv
import os

# Login credentials - replace these with actual credentials
EMAIL = "jaykrishnamishra23@gmail.com"
PASSWORD = "Gr@3691215"

async def search_job():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to Naukri
        await page.goto('https://www.naukri.com')
        print("Navigated to Naukri.com")

        # Login process
        try:
            # Click login button
            await page.click('a#login_Layer')
            print("Clicked login button")

            # Wait for the login form to load
            await page.wait_for_selector('form[name="login-form"]', timeout=10000)
            
            # Wait a bit for the form to be fully interactive
            await asyncio.sleep(2)
            
            # Fill email
            await page.fill('input[placeholder="Enter your active Email ID / Username"]', EMAIL)
            print("Filled email")
            
            # Fill password
            await page.fill('input[type="password"]', PASSWORD)
            print("Filled password")
            
            # Click the login submit button
            await page.click('button.loginButton')
            print("Clicked login button")

            # Wait for login to complete
            await page.wait_for_selector('div.nI-gNb-drawer__bars', timeout=30000)
            print("Login successful")

            # Wait for page to stabilize after login
            await asyncio.sleep(3)

        except Exception as e:
            print(f"Login failed: {str(e)}")
            await browser.close()
            return

        try:
            # Wait for search bar after login
            await page.wait_for_selector('.nI-gNb-search-bar input.suggestor-input', timeout=10000)
            print("Search bar found")
            await page.fill('.nI-gNb-search-bar input.suggestor-input', 'english teacher')
            print("Entered search term")
            # Click search button
            await page.click('.nI-gNb-sb__icon-wrapper')
            print("Clicked search")
             
            # Fill search term and hit enter
           # await page.fill('.nI-gNb-search-bar input.suggestor-input', 'devsecops engineer')
            await page.press('.nI-gNb-search-bar input.suggestor-input', 'Enter')
            print("Entered search term and pressed Enter")
                                                                    
            #await page.wait_for_timeout(1000)  # Wait for search to trigger

                                                                   
            # Wait for search results to load
            await page.wait_for_timeout(5000)
            await page.wait_for_selector('.srp-jobtuple-wrapper', timeout=30000)
            print("Search results loaded")
                    
                                                                    

            # Get top 5 job links
            job_links = await page.evaluate('''() => {
                const links = [];
                document.querySelectorAll('.srp-jobtuple-wrapper a.title').forEach((element, index) => {
                    if (index < 25) {
                        links.push(element.href);
                    }
                });
                return links;
            }''')

            print(f"Found {len(job_links)} job links")
            
            
            # Load OpenAI API key
            load_dotenv()
            client = OpenAI(api_key=os.getenv('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'))

            async def handle_questionnaire(page):
                try:
                    # Wait for questionnaire to appear
                    await page.wait_for_selector('.chatbot_MessageContainer', timeout=5000)
                    
                    # Extract question
                    question_text = await page.evaluate('''
                        () => document.querySelector('.botMsg.msg span').innerText
                    ''')
                    
                    # Get answer from OpenAI
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a job applicant. Answer job related questions professionally and honestly."},
                            {"role": "user", "content": f"How should I answer this job application question: {question_text}"}
                        ]
                    )
                    answer = response.choices[0].message.content

                    # Enter answer in input field
                    await page.wait_for_selector('#userInput__vi0egcg2jInputBox')
                    await page.evaluate(f'''
                        (answer) => {{
                            document.querySelector('#userInput__vi0egcg2jInputBox').innerText = answer
                        }}
                    ''', answer)

                    # Click save button
                    await page.click('.sendMsg')
                    await page.wait_for_timeout(2000)  # Wait for response

                except Exception as e:
                    print(f"Error in questionnaire: {str(e)}")


            # Open jobs concurrently
            async def open_job(link, index):
                try:
                    job_page = await context.new_page()
                    await job_page.goto(link)
                    print(f"Opened job {index + 1}")
                    
                    # Wait for and click Apply button
                    try:
                        await job_page.wait_for_selector('button#apply-button', timeout=5000)
                        await job_page.click('button#apply-button')
                        print(f"Applied to job {index + 1}")
                        await job_page.wait_for_timeout(2000)  # Wait for application to process
                    except Exception as e:
                        print(f"Could not apply to job {index + 1}: {str(e)}")
                        
                    return job_page
                except Exception as e:
                    print(f"Error opening job {index + 1}: {str(e)}")
               

            # Create tasks for all jobs
            tasks = [open_job(link, i) for i, link in enumerate(job_links)]
            
            # Run all tasks concurrently
            await asyncio.gather(*tasks)

            print("All jobs opened. Waiting 30 seconds before closing...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Error during search process: {str(e)}")
            try:
                await page.screenshot(path='search_error.png')
                print("Screenshot saved as search_error.png")
            except:
                print("Failed to take screenshot")

        finally:
            await browser.close()

if __name__ == '__main__':
    try:
        asyncio.run(search_job())
    except Exception as e:
        print(f"Main program error: {str(e)}")