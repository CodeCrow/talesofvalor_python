from Locators.element import (BaseCheckboxElement, BasePageElement,
                              IframeNotesElement)
from Locators.locators import AddEventLocators

from Pages.page import BasePage


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


class NotesIframe(IframeNotesElement):
    locator = "//p"
    IframeLocator = "//div[@id='cke_1_contents']/iframe"


class SummaryIframe(IframeNotesElement):
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
