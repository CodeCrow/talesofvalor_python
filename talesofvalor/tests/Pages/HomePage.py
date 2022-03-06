from Locators.locators import HomeLocators

from Pages.page import BasePage


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
