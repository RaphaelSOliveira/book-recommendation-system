import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class BBEScraper:
    # TODO - arrumar docmentação da classe
    """
    This is a class for scraping book information on a GoodReads (GR) list.

    Attributes:
        driver (WebDriver): The WebDriver used by selenium, will be initialized only when needed.
        book_links (list of dict): The list containing book urls, votes and scores taken from GR list.
        books (list of dict): The list of dictionarys containing book information scraped.
        broken (list of dict): The list of broken links in GR, useful to retry scraping.
        list_url (string): The URL of the target GR list to be scraped.
        chrome_options (Options): The driver options to be used by the WebDriver, including headless modes.
        robots_disallow (list of string): The list of URL disallowed in GR robots.txt
    """

    def __init__(self, chrome_options):
        """
        The constructor for BBEScraper class.

        :param driver_options: The driver options to replace defaults (optional).
        """
        self.driver = ""
        self.books = []
        self.n_books_per_page = 100
        self.n_pages = 100
        self.__BASE_BBE_URL = "https://www.goodreads.com/list/show/1.Best_Books_Ever?page="
        self.chrome_options = chrome_options


    def navigate_book_details(self, BBE_book_num:int) -> None:
        book_xpath = f"/html/body/div[2]/div[3]/div[1]/div[2]/div[3]/div[5]/table/tbody/tr[{BBE_book_num}]/td[3]/a/span"

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, book_xpath))
        ).click()
        
    def get_title(self) -> str:
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[1]/div[1]/h1"))
        )

        return elem.text

    def get_author(self) -> str:
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[1]/h3/div/span[1]/a/span"))
        )

        return elem.text

    def get_rating(self) -> float:
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[2]/a/div[1]/div"))
        )
        
        return float(elem.text)

    def get_summary(self) -> str:
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div/button"))
        ).click()

        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[1]/div/div/span"))
        )

        return elem.text

    def get_genres(self) -> list:
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[5]/ul/div/button"))
        ).click()
        
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[5]/ul"))
        )

        return elem.text.split("\n")[1:-1]
    
    def get_num_pages(self) -> str:
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[1]/span/div/p[1]"))
        )

        return str(re.findall("\\d+", elem.text)[0])

    def get_awards(self) -> list:
        return self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[2]/span")
        #try:
        #    try:
        #        self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[2]/span/div/div[1]/dd/div/div[2]/div/button").click()
                
        #    except:
        #        pass

        #    elem = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[2]/span/div/div[1]/dd/div")

        #except NoSuchElementException:
        #    return []

        #return elem.text.split(",")

    def expand_book_details_and_editions(self) -> None:
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/div/button").click()

    def exit_login_modal(self) -> None:
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[1]/div/div/button"))
        ).click()
    
    def navigate_url(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("https://www.goodreads.com/list/show/1.Best_Books_Ever?page=1")
        
    def extract_BBE_data(self) -> None:
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        bbe_pages_links = [f"{self.__BASE_BBE_URL}{bbe_page}" for bbe_page in range(1,self.n_pages + 1)]

        first_execution = True
        for bbe_page_link in bbe_pages_links:
            self.driver.get(bbe_page_link)
           
            time.sleep(2)
            self.driver.maximize_window()
            
            for i in range(0, self.n_books_per_page):
                try:
                    self.navigate_book_details(i)

                    # When navigating through Best Books Ever for the first time, a modal requiring login will appear
                    # This if closes login modal so a ElementClickInterceptedException error will not raise
                    if first_execution:
                        time.sleep(10)
                        self.exit_login_modal()
                        first_execution = False
                    
                    self.expand_book_details_and_editions()

                    book = {
                        "id" : self.driver.current_url,
                        "title" : self.get_title(),
                        "author" : self.get_author(),
                        "rating" : self.get_rating(),
                        "summary" : self.get_summary(),
                        "genres" : self.get_genres(),
                        "pages" : self.get_num_pages(),
                        "error" : None
                    }
        
                except ElementClickInterceptedException as e:
                    print("Error ElementClickInterceptedException: Element not clickable due to overlay")
                    book = {"id" : self.driver.current_url, "error" : f"{e}"}
                except NoSuchElementException as e:
                    print("Error NoSuchElementException")
                    book = {"id" : self.driver.current_url, "error" : f"{e}"}
                except TimeoutException as e:
                    print("Error TimeoutException")
                    book = {"id" : self.driver.current_url, "error" : f"{e}"}
                except Exception as e:
                    print(f"Unexpected error occurred: {e}")
                    book = {"id" : self.driver.current_url, "error" : f"{e}"}
                
                finally:
                    self.books.append(book)
        
        self.driver.close()
    
    #def load_BBE_data(self):

        

    
    