from selenium.webdriver.common.by import By


class MainPageLocators(object):
    """A class for main page locators. All main page locators should come here"""
    LoginLink = (By.XPATH, "//a[text()='Log In']")
    RegistationLink = (By.XPATH, "//a[text()='Register']")


class LoginLocators(object):
    """A class for main page locators. All main page locators should come here"""
    LoginBtn = (By.XPATH, "//input[@type='submit']")


class RegisterLocators(object):
    Save_Changes = (
        By.XPATH, "//button[@type='submit' and text()='Save changes']")


class SideBar(object):
    ActionMenu = (By.XPATH, "//div[@id='action_menu']")
    EventRegistrationLink = (By.XPATH, ".//a[text()='Registration']")
    EventList = (By.XPATH, ".//a[text()='List']")
    BasicInfoBackgrounds = (By.XPATH, ".//a[text()='Backgrounds']")
    BasicInfoHeaders = (By.XPATH, ".//a[text()='Headers']")
    BasicInfoSkills = (By.XPATH, ".//a[text()='Skills']")
    BasicInfoSkillsRules = (By.XPATH, ".//a[text()='Skill Rules']")
    StaffInfo = (By.XPATH, ".//ul[@id='navigation_action_staff']")
    PELS = (By.XPATH, ".//a[text()='PELS']")
    BGS = (By.XPATH, ".//a[text()='BGS']")
    Characters_New = (
        By.XPATH, ".//li[text()='Characters']/following-sibling::li[1]/a[text()='New']")
    Characters_List = (
        By.XPATH, ".//li[text()='Characters']/following-sibling::li[2]/a[text()='List']")


class HomeLocators(SideBar):
    LogoutLink = (
        By.XPATH, "//nav[@id='navigation_user']//a[text()='Log Out']")

class EventLocators(object):
    AddLink = (
        By.XPATH, "//div[@id='main_content']//a[contains(text(),'Add one')]")
    EventNames = (By.XPATH,"//table[@class='list']//td[1]//a")

class AddEventLocators(object):
    submitbutton = (By.XPATH,"//input[@type='submit']")

class RegForEventLocators(object):
    RegisterButton = (By.XPATH,"//input[@value='Register']")