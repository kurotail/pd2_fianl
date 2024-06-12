from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from localVals import SUDOKU_URL
from datetime import datetime
import asyncio
import bs4


class SudokuCrawler():
    
    def __init__(self, show_brower:bool = False) -> None:
        opts = webdriver.ChromeOptions()
        opts.add_argument("--no-sandbox")
        if show_brower == False:
            opts.add_argument("--headless=new")
        chrome_service=Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=chrome_service, options=opts)
        self.timeout = WebDriverWait(self.chrome, 10)
    
    def __del__(self) -> None:
        self.chrome.quit()
    
    async def crawlBoard(self, difficulty:int) -> list:
        """
        difficulty:0 -> Easy,
        difficulty:1 -> Medium,
        difficulty:2 -> Hard,
        difficulty:3 -> Expert
        
        return 2D-List of board
        """
        if difficulty > 3 or difficulty < 0:
            raise ValueError("Difficulty value must be between 0 and 3")
        
        self.chrome.switch_to.window(self.chrome.window_handles[0])
        self.chrome.execute_script(f"window.open('{SUDOKU_URL}')") #open url in new tab
        this_tab = self.chrome.window_handles[-1] #record this tab
        self.chrome.switch_to.window(this_tab) #switch to this tab
        self.timeout.until(EC.element_to_be_clickable((By.ID, "sudoku-level-name"))).click() #wait for tab loaded  and open difficulty choose modal
        self.chrome.find_elements(By.CLASS_NAME, "block-checkboxes__el")[difficulty].click() #click difficulty radio btn
        self.chrome.find_element(By.CLASS_NAME, "difficulty").click() #click confirm btn
        
        timerElement = self.chrome.find_element(By.XPATH, "//*[@id='sudokuTimer']/div/span") #get timer element
        while True: 
            timer_t = datetime.strptime(timerElement.text, "%M:%S")
            if timer_t.second > 0: #wait for sudoku table loaded
                break
            await asyncio.sleep(0.25)
            
        self.chrome.switch_to.window(this_tab) #switch to this tab
        soup = bs4.BeautifulSoup(self.chrome.page_source, 'html.parser') #parse to soup
        self.chrome.close() #close this tab
        tds = soup.find_all("td")
        board = [[0]*9 for i in range(9)]
        for i in range(81):
            if len(tds[i]['class']) == 4:
                board[i//9][i%9] = int(tds[i].find("span").text)
        return board
    
if __name__ == "__main__":
    sudoku_crawler = SudokuCrawler()
    sudoku_crawler.crawlBoard(1)