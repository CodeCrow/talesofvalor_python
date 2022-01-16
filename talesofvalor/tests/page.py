from element import BasePageElement
from locators import MainPageLocators
from locators import LoginLocators
from locators import RegisterLocators
class UsernameElement(BasePageElement):
    locator = "//input[@name='username']"

class PasswordElement(BasePageElement):
    locator = "//input[@name='password']"
class PasswordConfirmElement(BasePageElement):
    locator = "//input[@name='password_confirm']"

class FirstNameElement(BasePageElement):
    locator = "//input[@name='first_name']"

class LastNameElement(BasePageElement):
    locator = "//input[@name='last_name']"

class PlayerPronounsElement(BasePageElement):
    locator = "//input[@name='player_pronouns']"

class EmailElement(BasePageElement):
    locator = "//input[@name='email']"

class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver):
        self.driver = driver

class MainPage(BasePage):
    """Home page action methods come here"""

    def is_title_matches(self,title):
        return title in self.driver.title

    def click_login(self):
        element = self.driver.find_element(*MainPageLocators.LoginLink)
        element.click()
    def click_register(self):
        element = self.driver.find_element(*MainPageLocators.RegistationLink)
        element.click()

class LogInPage(BasePage):
    username = UsernameElement()
    password = PasswordElement()
    def is_title_matches(self,title):
        return title in self.driver.title

    def click_login_btn(self):
        element = self.driver.find_element(*LoginLocators.LoginBtn)
        element.click()

class RegisterPage(BasePage):
    firstname = FirstNameElement()
    lastName = LastNameElement()
    username = UsernameElement()
    password = PasswordElement()
    passwordConfirm = PasswordConfirmElement()
    email = EmailElement()
    Pronouns = PlayerPronounsElement()

    def click_save_changes_btn(self):
        element = self.driver.find_element(*RegisterLocators.Save_Changes)
        element.click()