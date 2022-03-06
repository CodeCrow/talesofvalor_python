import sys
import time
import unittest
import uuid
from datetime import date

import names
from dateutil.relativedelta import relativedelta
from mailosaur import MailosaurClient
from selenium import webdriver
from selenium.webdriver.common.by import By

import Pages.AddEventPage as AddEventPage
import Pages.EventsPage as EventsPage
import Pages.HomePage as HomePage
import Pages.LoginPage as LoginPage
import Pages.MainPage as MainPage
import Pages.RegForEventPage as EventRegPage
import Pages.RegisterPage as RegPage


class TOVTests(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.mailosaur = MailosaurClient("0rKzKCj7G8x58VZQ")
        self.emailDomain = "xpfj38ez.mailosaur.net"
        self.PaypalInfo = {"FirstName": "John",
                           "LastName": "Doe",
                           "Email": "sb-n4bto12352567@personal.example.com",
                           "Password": "5jV}y2}>"}
        return super().setUp()

    def test_Login(self, username="animefreak4242", password="4Tdi5d$?&yT$ELEQ"):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = LoginPage.LogInPage(self.driver)
        LIPage.username = username
        LIPage.password = password
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." not in self.driver.page_source)
        header = self.driver.find_element(By.XPATH, "//h1")
        self.assertTrue(header.text == username)

    def test_Bad_Password(self):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = LoginPage.LogInPage(self.driver)
        LIPage.username = "timtp"
        LIPage.password = "asti6464"
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." in self.driver.page_source)

    def test_Bad_Username(self):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = LoginPage.LogInPage(self.driver)
        LIPage.username = "BadUser"
        LIPage.password = "Asti6464"
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." in self.driver.page_source)

    def test_duplicate_registration(self):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = RegPage.RegisterPage(self.driver)
        reg_page.firstname = "Tim"
        reg_page.lastName = "Plummer"
        reg_page.Pronouns = "he/him"
        reg_page.email = "animefreak4242+test@gmail.com"
        reg_page.username = "animefreak4242"
        reg_page.password = "4Tdi5d$?&yT$ELEQ"
        reg_page.passwordConfirm = "4Tdi5d$?&yT$ELEQ"
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "IntegrityError at /en/players/register/" in self.driver.page_source)
        # TODO update this for when the error page for duplicate username/email is active

    def test_random_registration(self, username=str(uuid.uuid4())[:8], password=str(uuid.uuid4())[:15]):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = RegPage.RegisterPage(self.driver)
        reg_page.firstname = names.get_first_name()
        reg_page.lastName = names.get_last_name()
        self.email =  reg_page.firstname +reg_page.lastName +username+"@"+self.emailDomain
        reg_page.email = self.email
        reg_page.Pronouns = "they/them"
        self.username = username
        reg_page.username = self.username
        self.password = password
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()

    def test_missingInfo_registration(self, username=str(uuid.uuid4())[:8], password=str(uuid.uuid4())[:15]):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = RegPage.RegisterPage(self.driver)
        reg_page.lastName = "McTester"
        reg_page.email = "tester.McTester@"+self.emailDomain
        reg_page.Pronouns = "they/them"
        self.username = username
        reg_page.username = self.username
        self.password = password
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.firstname = "Tester"
        reg_page.lastName = ""
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.lastName = "McTester"
        reg_page.email = ""
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.email = "tester.McTester@"+self.emailDomain
        reg_page.Pronouns = ""
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.Pronouns = "they/them"
        reg_page.username = ""
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)

    def test_bademail_registration(self, username=str(uuid.uuid4())[:8], password=str(uuid.uuid4())[:15]):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = RegPage.RegisterPage(self.driver)
        reg_page.firstname = "Tester"
        reg_page.lastName = "McTester"
        reg_page.email = "tester.McTester"
        reg_page.Pronouns = "they/them"
        self.username = username
        reg_page.username = self.username
        self.password = password
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.email = "tester.McTester@"
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        reg_page.email = "tester.McTester@company"
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        self.assertTrue(
            "Enter a valid email address." in self.driver.page_source)

    def test_badpassword_registration(self, username=str(uuid.uuid4())[:8], password=str(uuid.uuid4())[:15]):
        main_page = MainPage.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = RegPage.RegisterPage(self.driver)
        reg_page.firstname = "Tester"
        reg_page.lastName = "McTester"
        self.email = "tester.McTester@"+self.emailDomain
        reg_page.email = self.email
        reg_page.Pronouns = "they/them"
        self.username = username
        reg_page.username = self.username
        self.password = password
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password+"2"
        reg_page.click_save_changes_btn()
        self.assertTrue(
            "<h1>Register as a new user.</h1>" in self.driver.page_source)
        self.assertTrue(
            "The two password fields must match." in self.driver.page_source)

    def test_login_admin(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = HomePage.HomePage(self.driver)

    def test_click_register(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_Registration()
        self.assertTrue(
            ("<h1>Register for events</h1>" in self.driver.page_source) | ("<h1>No scheduled events at this time.</h1>" in self.driver.page_source))

    def test_click_EventList(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_EventList()
        self.assertTrue("<h1>Events</h1>" in self.driver.page_source)

    def test_click_BasicInfo_Backgrounds(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_BasicInfo_Backgrounds()
        self.assertTrue("<h1>Origins</h1>" in self.driver.page_source)

    def test_click_BasicInfo_Headers(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_BasicInfo_Headers()
        self.assertTrue("<h1>Headers</h1>" in self.driver.page_source)

    def test_click_BasicInfo_Skills(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_BasicInfo_Skills()
        self.assertTrue("<h1>Skills</h1>" in self.driver.page_source)

    def test_click_BasicInfo_SkillsRules(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_BasicInfo_SkillRules()
        self.assertTrue("<h1>Rules</h1>" in self.driver.page_source)

    def test_click_PELS(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_StaffInfo_PELS()
        self.assertTrue("<h1>PELs</h1>" in self.driver.page_source)

    def test_click_BGS(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_StaffInfo_BGS()
        self.assertTrue(
            "<h1>Between Game Skills</h1>" in self.driver.page_source)

    def test_addEvent(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = HomePage.HomePage(self.driver)
        home.click_EventList()
        self.assertTrue("<h1>Events</h1>" in self.driver.page_source)
        events = EventsPage.EventsPage(self.driver)
        nextEvent = events.get_nextEvent()
        events.click_addOne()
        addEvent = AddEventPage.AddEventPage(self.driver)
        addEvent.eventName = nextEvent
        eventdate = date.today()+relativedelta(months=2)
        pelDate = date.today()+relativedelta(months=2, days=14)
        bgsDate = date.today()+relativedelta(months=2, days=14)
        addEvent.eventDate = eventdate.strftime("%m/%d/%Y")
        addEvent.PELDate = pelDate.strftime("%m/%d/%Y")
        addEvent.BGSDate = bgsDate.strftime("%m/%d/%Y")
        addEvent.Notes = "This is a MAJOR test"
        addEvent.Summary = """Lets see if multiple lines will input as well. 
        This is line 1 
        this is line 2"""
        addEvent.click_submit()
        self.assertTrue(nextEvent in self.driver.page_source)

    def test_registerForNextEvent(self):
        self.test_random_registration()
        home = HomePage.HomePage(self.driver)
        home.click_Registration()
        self.assertTrue(
            ("<h1>Register for events</h1>" in self.driver.page_source))
        EventReg = EventRegPage.RegForEventPage(self.driver)
        EventReg.Make = "Toyota"
        EventReg.Model = "Corolla"
        EventReg.Color = "Black"
        EventReg.VehReg = str(uuid.uuid4())[:8]
        EventReg.Contact = str(uuid.uuid4())[:7]
        EventReg.Notes = """Test to see if multilines will work
        Line 2
        Line 3"""
        EventReg.button = ("Spring 1 2022",True)
        EventReg.ClickRegister()

        
    def tearDown(self) -> None:
        # so that you can view the final page for a second before the page closes.
        time.sleep(0.5)
        self.driver.close()
        self.driver.quit()
        return super().tearDown()


def main(out=sys.stderr, verbosity=2):
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity=verbosity).run(suite)


if __name__ == '__main__':
    with open('testing.out', 'w') as f:
        main(f)
