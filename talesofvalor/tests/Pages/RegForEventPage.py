from Locators.element import BasePageElement, BaseRadioElement
from Locators.locators import RegForEventLocators

from Pages.page import BasePage


class VehicalMake(BasePageElement):
    locator = "//input[@name='vehicle_make']"


class VehicalModel(BasePageElement):
    locator = "//input[@name='vehicle_model']"


class VehicalColor(BasePageElement):
    locator = "//input[@name='vehicle_color']"


class VehicalReg(BasePageElement):
    locator = "//input[@name='vehicle_registration']"


class LocalContact(BasePageElement):
    locator = "//input[@name='local_contact']"


class Notes(BasePageElement):
    locator = "//textarea[@name='notes']"


class EventRadioButton(BaseRadioElement):
    _locator =""
    def locator(self,name:str) ->str:
        self._locator = f"//tr[td/input[@type='radio']][contains(.,'{name}')]//input"
        return self._locator

class RegForEventPage(BasePage):
    Make = VehicalMake()
    Model = VehicalModel()
    Color = VehicalColor()
    VehReg = VehicalReg()
    Contact = LocalContact()
    Notes = Notes()
    button = EventRadioButton()

    def ClickRegister(self) -> None:
        Register = self.driver.find_element(
            *RegForEventLocators.RegisterButton)
        if Register is not None:
            Register.click()
