import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
#from browser_use.browser.config import BrowserConfig
from typing import Optional
from browser_use import BrowserConfig
from browser_use import Browser
load_dotenv()

EMAIL = "jaykrishnamishra23@gmail.com"
PASSWORD = "Gr@3691215"


browser = Browser()
    

async def login_to_naukri(browser: Browser) -> Optional[bool]:
    """Handle login process using browser_use Browser"""
    try:
        page = await browser.new_page()
        await page.goto('https://www.naukri.com')
        print("Navigated to Naukri.com")

        # Click login button
        await page.click('a#login_Layer')
        print("Clicked login button")

        # Wait for login form
        await page.wait_for_selector('form[name="login-form"]')
        await asyncio.sleep(2)

        # Fill credentials
        await page.fill('input[placeholder="Enter your active Email ID / Username"]', EMAIL)
        print("Filled email")
        await page.fill('input[type="password"]', PASSWORD)
        print("Filled password")

        # Submit login
        await page.click('button.loginButton')
        print("Clicked login button")

        # Wait for successful login
        await page.wait_for_selector('div.nI-gNb-drawer__bars')
        print("Login successful")
        await asyncio.sleep(3)
        
        return True

    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

async def search_jobs(browser: Browser) -> Optional[bool]:
    """Handle job search process"""
    try:
        page = await browser.current_page()
        
        # Wait for and use search bar
        await page.wait_for_selector('.nI-gNb-search-bar input.suggestor-input')
        print("Search bar found")
        
        await page.fill('.nI-gNb-search-bar input.suggestor-input', 'devsecops engineer')
        print("Entered search term")
        
        await page.click('.nI-gNb-sb__icon-wrapper')
        print("Clicked search")
        
        await page.press('.nI-gNb-search-bar input.suggestor-input', 'Enter')
        print("Entered search term and pressed Enter")
        
        await asyncio.sleep(5)  # Wait for results to load
        return True

    except Exception as e:
        print(f"Search failed: {str(e)}")
        return False

async def main():
    try:
        # Initialize browser
     
        
        # Initialize LLM
        model = model='gpt-4o'

        # Login process
        if not await login_to_naukri(browser):
            #await browser.close()
            return

        # Search process
        if not await search_jobs(browser):
            #await browser.close()
            return

        # Create Agent for job application
        jobapply = Agent(
            task='On the existing browser tab that open, search for apply button and click on apply',
            llm=model,
            browser=browser
        )

        await jobapply.run()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Byee")
        #await browser.close()

if __name__ == "__main__":
    asyncio.run(main())