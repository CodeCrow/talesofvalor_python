import re

from Locators.locators import EventLocators

from Pages.page import BasePage


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
