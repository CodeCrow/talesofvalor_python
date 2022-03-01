from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class BasePageElement(object):
    """Base page class that is initialized on every page object class."""

    def __set__(self, obj, value: str) -> None:
        """Sets the text to the value supplied"""

        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        driver.find_element(By.XPATH, self.locator).clear()
        driver.find_element(By.XPATH, self.locator).send_keys(value)

    def __get__(self, obj: object, owner) -> str:
        """Gets the text of the specified object"""

        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        element = driver.find_element(By.XPATH, self.locator)
        return element.get_attribute("value")

class BaseCheckboxElement(object):
    """Base page class that is initialized on every page object class."""

    def __set__(self, obj, value: bool) -> None:
        """Sets the text to the value supplied"""

        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        result = driver.find_element(By.XPATH, self.locator).is_selected()
        if not result and value:
            driver.find_element(By.XPATH, self.locator).click()
        elif result and not value:
            driver.find_element(By.XPATH, self.locator).click()

    def __get__(self, obj: object, owner) -> bool:
        """Gets the value of the specified object"""

        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        element = driver.find_element(By.XPATH, self.locator)
        return element.is_selected()


class IframeElement(object):
    def __set__(self,obj, value:str)-> None:
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.IframeLocator))
        driver.switch_to.frame(driver.find_element(By.XPATH,self.IframeLocator))
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        driver.find_element(By.XPATH, self.locator).clear()
        driver.find_element(By.XPATH, self.locator).send_keys(value)
        driver.switch_to.default_content()

    def __get__(self,obj:object, owner)-> str:
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.IframeLocator))
        driver.switch_to.frame(driver.find_element(By.XPATH,self.IframeLocator))
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, self.locator))
        output = driver.page_source
        driver.switch_to.default_content()
        return output

class BaseRadioElement(object):
    """Base page class that is initialized on every page object class."""
    def __set__(self, obj, value: tuple) -> None:
        """Sets the text to the value supplied"""
        path = self.locator(value[0])
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, path))
        result = driver.find_element(By.XPATH, path).is_selected()
        if not result and value[1]:
            driver.find_element(By.XPATH, path).click()
        elif result and not value[1]:
            driver.find_element(By.XPATH, path).click()

    def __get__(self, obj: object, owner) -> tuple:
        """Gets the value of the specified object"""
        path = self._locator
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(By.XPATH, path))
        element = driver.find_element(By.XPATH, path)
        return element.is_selected()