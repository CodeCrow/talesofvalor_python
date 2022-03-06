from selenium import webdriver
from Locators.element import BaseCheckboxElement, BasePageElement, IframeNotesElement, BaseRadioElement
from Locators.locators import AddEventLocators, EventLocators, MainPageLocators, RegForEventLocators
from Locators.locators import LoginLocators
from Locators.locators import RegisterLocators
from Locators.locators import HomeLocators
from Pages.page import BasePage

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


class RegisterPage(BasePage):
    firstname = FirstNameElement()
    lastName = LastNameElement()
    username = UsernameElement()
    password = PasswordElement()
    passwordConfirm = PasswordConfirmElement()
    email = EmailElement()
    Pronouns = PlayerPronounsElement()

    def click_save_changes_btn(self) -> None:
        element = self.driver.find_element(*RegisterLocators.Save_Changes)
        element.click()