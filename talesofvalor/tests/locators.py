from typing import ClassVar
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

class SideBar(object):
    ActionMenu = (By.XPATH,"//div[@id='action_menu']")
    EventRegistrationLink = (By.XPATH,".//a[text()='Registration']")
    EventList = (By.XPATH,".//a[text()='List']")
    BasicInfoBackgrounds = (By.XPATH,".//a[text()='Backgrounds']")
    BasicInfoHeaders = (By.XPATH,".//a[text()='Headers']")
    BasicInfoSkills = (By.XPATH,".//a[text()='Skills']")
    BasicInfoSkillsRules = (By.XPATH,".//a[text()='Skill Rules']")
    StaffInfo = (By.XPATH,".//ul[@id='navigation_action_staff']")
    PELS= (By.XPATH,".//a[text()='PELS']")

class HomeLocators(SideBar):
    LogoutLink =(By.XPATH,"//nav[@id='navigation_user']//a[text()='Log Out']")

