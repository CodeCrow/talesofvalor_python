from Locators.element import BasePageElement
from Locators.locators import LoginLocators

from Pages.page import BasePage


class UsernameElement(BasePageElement):
    locator = "//input[@name='username']"


class PasswordElement(BasePageElement):
    locator = "//input[@name='password']"

        
class LogInPage(BasePage):
    username = UsernameElement()
    password = PasswordElement()

    def is_title_matches(self, title: str) -> bool:
        return title in self.driver.title

    def click_login_btn(self) -> None:
        element = self.driver.find_element(*LoginLocators.LoginBtn)
        element.click()
