from selenium import webdriver
from element import BasePageElement
from locators import MainPageLocators
from locators import LoginLocators
from locators import RegisterLocators
from locators import HomeLocators
from typing import Union

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

    def __init__(self, driver:webdriver.Chrome) -> None:
        self.driver = driver

class MainPage(BasePage):
    """Home page action methods come here"""

    def is_title_matches(self,title) -> bool:
        return title in self.driver.title

    def click_login(self) -> None:
        element = self.driver.find_element(*MainPageLocators.LoginLink)
        element.click()
    def click_register(self) -> None:
        element = self.driver.find_element(*MainPageLocators.RegistationLink)
        element.click()

class LogInPage(BasePage):
    username = UsernameElement()
    password = PasswordElement()
    def is_title_matches(self,title: str) -> bool:
        return title in self.driver.title

    def click_login_btn(self) -> None:
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

    def click_save_changes_btn(self) -> None:
        element = self.driver.find_element(*RegisterLocators.Save_Changes)
        element.click()
        
class HomePage(BasePage):
    def click_Logout(self) -> None:
        element = self.driver.find_element(*HomeLocators.LogoutLink)
        element.click()
    def click_Registration(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.EventRegistrationLink)
        element.click()
    def click_EventList(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.EventList)
        element.click()
    def click_BasicInfo_Backgrounds(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.BasicInfoBackgrounds)
        element.click()
    def click_BasicInfo_Headers(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.BasicInfoHeaders)
        element.click()
    def click_BasicInfo_Skills(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.BasicInfoSkills)
        element.click()
    def click_BasicInfo_SkillRules(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        element = actionMenu.find_element(*HomeLocators.BasicInfoSkillsRules)
        element.click()
    def click_StaffInfo_PELS(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        staffInfo = actionMenu.find_element(*HomeLocators.StaffInfo)
        if staffInfo is not None:
            PELS = staffInfo.find_element(*HomeLocators.PELS)
            PELS.click()