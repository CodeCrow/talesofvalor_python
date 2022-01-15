from logging import warn
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time 
import page

class TOVTests(unittest.TestCase):
    
    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.implicitly_wait(5)
        return super().setUp()
    
    def test_Login(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches("Tales of Valor : Fellowship" ))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = "timtp"
        LIPage.password = "Asti6464"
        LIPage.click_login_btn()
        self.assertTrue("Your username and password didn't match. Please try again." not in self.driver.page_source)
        header = self.driver.find_element(By.XPATH,"//h1")
        self.assertTrue(header.text == "timtp")
        
    def test_Bad_Password(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches("Tales of Valor : Fellowship" ))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = "timtp"
        LIPage.password = "asti6464"
        LIPage.click_login_btn()
        self.assertTrue("Your username and password didn't match. Please try again." in self.driver.page_source)

    def test_Bad_Username(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches("Tales of Valor : Fellowship" ))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = "BadUser"
        LIPage.password = "Asti6464"
        LIPage.click_login_btn()
        self.assertTrue("Your username and password didn't match. Please try again." in self.driver.page_source)
        

    def tearDown(self) -> None:
        time.sleep(1) #so that you can view the final page for a second before the page closes.
        self.driver.close()
        return super().tearDown()
    
if __name__ == "__main__":
    unittest.main()
