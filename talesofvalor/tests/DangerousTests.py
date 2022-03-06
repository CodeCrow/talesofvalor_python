import time
import unittest

from mailosaur import MailosaurClient
from selenium import webdriver

import Pages.HomePage as HomePage
from SimpleTests import TOVTests


class TOVDangerousTests(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.implicitly_wait(5)
        self.mailosaur = MailosaurClient("0rKzKCj7G8x58VZQ")
        self.emailDomain = "xpfj38ez.mailosaur.net"
        return super().setUp()

    def test_Generate_n_Users(self, n: int = 2, usernamePrefix="Tester_", password="asti6464"):
        u = 0
        for i in range(1, n+1):
            create_user = False
            while (create_user == False):
                if i+u < 10:
                    TOVTests.test_random_registration(
                        self, username=usernamePrefix+"0"+str(i+u), password=password)
                else:
                    TOVTests.test_random_registration(
                        self, username=usernamePrefix+str(i+u), password=password)

                if "IntegrityError at /en/players/register/" not in self.driver.page_source:
                    print(self.username+":"+self.password)
                    home = HomePage.HomePage(self.driver)
                    home.click_Logout()
                    create_user = True
                else:
                    u = u+1
                    self.driver.get("http://127.0.0.1:8000/")

    def tearDown(self) -> None:
        # so that you can view the final page for a second before the page closes.
        time.sleep(1)
        self.driver.close()
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
