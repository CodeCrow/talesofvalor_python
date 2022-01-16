from selenium.webdriver.common.by import By

class MainPageLocators(object):
    """A class for main page locators. All main page locators should come here"""
    LoginLink = (By.XPATH, "//a[text()='Log In']")
    RegistationLink = (By.XPATH,"//a[text()='Register']")
class LoginLocators(object):
    """A class for main page locators. All main page locators should come here"""
    LoginBtn = (By.XPATH, "//input[@type='submit']")
class RegisterLocators(object):
    Save_Changes = (By.XPATH,"//button[@type='submit' and text()='Save changes']")