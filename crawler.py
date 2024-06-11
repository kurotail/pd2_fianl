from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager
from localVals import SUDOKU_URL
import asyncio
import bs4

class SudokuCrawler():
    
    def __init__(self) -> None:
        opt = webdriver.ChromeOptions()
        opt.add_argument("--no-sandbox")
        # opt.add_argument("--headless=new")
        chrome_service=Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=chrome_service, options=opt)
        self.timeout = WebDriverWait(self.chrome, 10)
        self.chrome.get(SUDOKU_URL)
    
    def __del__(self) -> None:
        self.chrome.quit()
    
    def crawlBoard(self, difficulty:int) -> list:
        """
        difficulty:0 -> Easy,
        difficulty:1 -> Medium,
        difficulty:2 -> Hard,
        difficulty:3 -> Expert
        
        return 2D-List of board
        """
        self.chrome.find_element(By.ID, "sudoku-level-name").click() #open difficulty choose modal
        self.chrome.find_elements(By.CLASS_NAME, "block-checkboxes__el")[difficulty].click() #click difficulty radio btn
        self.chrome.find_element(By.CLASS_NAME, "difficulty").click() #click confirm btn
        soup = bs4.BeautifulSoup(self.chrome.page_source, 'html.parser')
        tds = soup.find_all("td")
        board = [[0]*9 for i in range(9)]
        for i in range(81):
            if len(tds[i]['class']) == 4:
                board[i//9][i%9] = int(tds[i].find("span").text)
        return board
    
    
if __name__ == "__main__":
    sudoku_crawler = SudokuCrawler()
    sudoku_crawler.crawlBoard(1)