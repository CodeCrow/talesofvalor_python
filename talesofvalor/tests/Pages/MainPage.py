from Locators.locators import MainPageLocators

from Pages.page import BasePage


class MainPage(BasePage):
    """Home page action methods come here"""

    def is_title_matches(self, title) -> bool:
        return title in self.driver.title

    def click_login(self) -> None:
        element = self.driver.find_element(*MainPageLocators.LoginLink)
        element.click()

    def click_register(self) -> None:
        element = self.driver.find_element(*MainPageLocators.RegistationLink)
        element.click()
