from selenium.webdriver.common.by import By

class MainPageLocators(object):
    """A class for main page locators. All main page locators should come here"""

    LoginLink = (By.XPATH, "//a[text()='Log In']")

class LoginLocators(object):
    """A class for main page locators. All main page locators should come here"""
    
    LoginBtn = (By.XPATH, "//input[@type='submit']")
    
class SearchResultsPageLocators(object):
    """A class for search results locators. All search results locators should
    come here"""

    pass