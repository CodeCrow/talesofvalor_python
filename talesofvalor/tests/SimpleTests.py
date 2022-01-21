import sys
import time
import unittest
import uuid
from logging import warn

from mailosaur import MailosaurClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import page


class TOVTests(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.implicitly_wait(5)
        self.mailosaur = MailosaurClient("0rKzKCj7G8x58VZQ")
        self.emailDomain = "xpfj38ez.mailosaur.net"
        return super().setUp()

    def test_Login(self, username="animefreak4242", password="4Tdi5d$?&yT$ELEQ"):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = username
        LIPage.password = password
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." not in self.driver.page_source)
        header = self.driver.find_element(By.XPATH, "//h1")
        self.assertTrue(header.text == username)

    def test_Bad_Password(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = "timtp"
        LIPage.password = "asti6464"
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." in self.driver.page_source)

    def test_Bad_Username(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_login()
        LIPage = page.LogInPage(self.driver)
        LIPage.username = "BadUser"
        LIPage.password = "Asti6464"
        LIPage.click_login_btn()
        self.assertTrue(
            "Your username and password didn't match. Please try again." in self.driver.page_source)

    def test_duplicate_registration(self):
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = page.RegisterPage(self.driver)
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
        main_page = page.MainPage(self.driver)
        self.assertTrue(main_page.is_title_matches(
            "Tales of Valor : Fellowship"))
        main_page.click_register()
        reg_page = page.RegisterPage(self.driver)
        reg_page.firstname = "Tester"
        reg_page.lastName = "McTester"
        reg_page.email = "tester.McTester@"+self.emailDomain
        reg_page.Pronouns = "they/them"
        self.username = username
        reg_page.username = self.username
        self.password = password
        reg_page.password = self.password
        reg_page.passwordConfirm = self.password
        reg_page.click_save_changes_btn()

    def test_login_admin(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = page.HomePage(self.driver)

    def test_click_register(self):
        self.test_Login(username="timtp", password="Asti6464")
        home = page.HomePage(self.driver)
        home.click_Registration()
        self.assertTrue("Register for events" in self.driver.page_source)

    def test_click_PELS(self):
        self.test_Login(username="timtp2", password="Asti6464")
        home = page.HomePage(self.driver)
        home.click_StaffInfo_PELS()

    def tearDown(self) -> None:
        # so that you can view the final page for a second before the page closes.
        time.sleep(1)
        self.driver.close()
        return super().tearDown()


def main(out=sys.stderr, verbosity=2):
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity=verbosity).run(suite)


if __name__ == '__main__':
    with open('testing.out', 'w') as f:
        main(f)
