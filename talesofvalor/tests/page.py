from distutils.log import error
from msilib.schema import Class
from xml.sax.xmlreader import Locator
from selenium import webdriver
from element import BaseCheckboxElement, BasePageElement, IframeElement
from locators import AddEventLocators, EventLocators, MainPageLocators
from locators import LoginLocators
from locators import RegisterLocators
from locators import HomeLocators
import re


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

    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver


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


class LogInPage(BasePage):
    username = UsernameElement()
    password = PasswordElement()

    def is_title_matches(self, title: str) -> bool:
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

    def click_StaffInfo_BGS(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        staffInfo = actionMenu.find_element(*HomeLocators.StaffInfo)
        if staffInfo is not None:
            BGS = staffInfo.find_element(*HomeLocators.BGS)
            BGS.click()

    def click_Characters_New(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        staffInfo = actionMenu.find_element(*HomeLocators.StaffInfo)
        if staffInfo is not None:
            Char_New = staffInfo.find_element(*HomeLocators.Characters_New)
            Char_New.click()

    def click_Characters_New(self) -> None:
        actionMenu = self.driver.find_element(*HomeLocators.ActionMenu)
        staffInfo = actionMenu.find_element(*HomeLocators.StaffInfo)
        if staffInfo is not None:
            Char_List = staffInfo.find_element(*HomeLocators.Characters_List)
            Char_List.click()


class EventNameElement(BasePageElement):
    locator = "//input[@name='name']"


class EventDateElement(BasePageElement):
    locator = "//input[@name='event_date']"


class PELDateElement(BasePageElement):
    locator = "//input[@name='pel_due_date']"


class BGSDateElement(BasePageElement):
    locator = "//input[@name='bgs_due_date']"


class OOGEventCheckbox(BaseCheckboxElement):
    locator = "//input[@id='id_oog_p']"


class NotesIframe(IframeElement):
    locator = "//p"
    IframeLocator = "//div[@id='cke_1_contents']/iframe"


class SummaryIframe(IframeElement):
    locator = "//p"
    IframeLocator = "//div[@id='cke_2_contents']/iframe"


class AddEventPage(BasePage):
    eventName = EventNameElement()
    eventDate = EventDateElement()
    PELDate = PELDateElement()
    BGSDate = BGSDateElement()
    OOGEvent = OOGEventCheckbox()
    Notes = NotesIframe()
    Summary = SummaryIframe()

    def click_submit(self) -> None:
        submitButton = self.driver.find_element(*AddEventLocators.submitbutton)
        if submitButton is not None:
            submitButton.click()


class EventsPage(BasePage):

    def click_addOne(self) -> None:
        AddLink = self.driver.find_element(*EventLocators.AddLink)
        if AddLink is not None:
            AddLink.click()

    def get_nextEvent(self) -> str:
        eventList = self.driver.find_elements(*EventLocators.EventNames)
        ptrn = "(Spring|Fall) ([0-9]+) ([0-9]*)"
        maxyear = 0
        for eventName in eventList:
            matchSuccess = re.match(ptrn, eventName.text)
            if matchSuccess is not None:
                x = re.search(ptrn, eventName.text)
                maxyear = max(int(x.group(3)), maxyear)
        maxevent = {"Fall": 0, "Spring": 0}
        for eventName in eventList:
            if str(maxyear) in eventName.text:
                matchSuccess = re.match(ptrn, eventName.text)
                if matchSuccess is not None:
                    x = re.search(ptrn, eventName.text)
                    maxevent[x.group(1)] = max(
                        int(x.group(2)), maxevent[x.group(1)])
        if maxevent["Spring"] == 2:
            nextSeason = "Fall"
        else:
            nextSeason = "Spring"
        nextNumber = maxevent[nextSeason]+1
        if nextNumber == 3:
            nextNumber = 1
            if nextSeason == 'Spring':
                nextSeason = 'Fall'
                next_year = maxyear
            else:
                nextSeason = 'Spring'
                next_year = maxyear + 1
        else:
            next_year = maxyear
        next_event_name = '%s %d %d' % (nextSeason, nextNumber, next_year)
        return next_event_name
