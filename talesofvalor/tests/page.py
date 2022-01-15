from element import BasePageElement
from locators import MainPageLocators
from locators import LoginLocators

class UsernameElement(BasePageElement):
    """This class gets the search text from the specified locator"""
    locator = "//input[@name='username']"

class PasswordElement(BasePageElement):
    """This class gets the search text from the specified locator"""
    locator = "//input[@name='password']"

class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver):
        self.driver = driver

class MainPage(BasePage):
    """Home page action methods come here"""

    #Declares a variable that will contain the retrieved text
    def is_title_matches(self,title):
        """Verifies that the "Python" appears in page title"""

        return title in self.driver.title

    def click_login(self):
        """Triggers the search"""

        element = self.driver.find_element(*MainPageLocators.LoginLink)
        element.click()

class LogInPage(BasePage):
    """Home page action methods come here"""

    #Declares a variable that will contain the retrieved text
    username = UsernameElement()
    password = PasswordElement()
    def is_title_matches(self,title):
        """Verifies that the "Python" appears in page title"""

        return title in self.driver.title

    def click_login_btn(self):
        """Triggers the search"""

        element = self.driver.find_element(*LoginLocators.LoginBtn)
        element.click()

class SearchResultsPage(BasePage):
    """Search results page action methods come here"""

    def is_login_success(self):
        # Probably should search for this text in the specific page
        # element, but as for now it works fine
        return "No results found." not in self.driver.page_source