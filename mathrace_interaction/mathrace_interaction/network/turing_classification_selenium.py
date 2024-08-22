# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""A selenium browser that connects to a classification page on the current live turing instance."""

import typing
import urllib.parse

import bs4
import requests
import selenium.common.exceptions
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.remote.webdriver
import selenium.webdriver.remote.webelement
import selenium.webdriver.support.expected_conditions as EC  # noqa: N812
import selenium.webdriver.support.ui

import mathrace_interaction.time


class TuringClassificationSelenium:
    """
    A selenium browser that connects to a classification page on the current live turing instance.

    Parameters
    ----------
    root_url
        URL of the root of the turing website.
    race_id
        The ID of the turing race to follow.
    max_wait
        Maximum amount to wait in seconds for the requested page to load fully.

    Attributes
    ----------
    _browser
        The selenium browser that will be used to connect to the website.
    _root_url
        URL of the root of the turing website.
    _race_id
        The ID of the turing race to follow.
    _max_wait
        Maximum amount to wait in seconds for the requested page to load fully.
    _locked
        If unlocked (False), the browser is free to update the page, e.g. due to changes triggered by javascript.
        If locked (True), the web page seen by this class is frozen, and updates are not reflected in its content.
    _locked_page_source
        If locked, it contains the HTML source at time of locking.
        If unlocked, it contains None.
    _locked_page_soup
        If locked, it contains a BeautifulSoup object to parse the HTML source at time of locking.
        If unlocked, it contains None.
    """

    def __init__(self, root_url: str, race_id: int, max_wait: int) -> None:
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")  # type: ignore[no-untyped-call]
        options.add_argument("--window-size=1920,1080")  # type: ignore[no-untyped-call]
        options.add_argument("--headless")  # type: ignore[no-untyped-call]
        options.add_argument("--disable-gpu")  # type: ignore[no-untyped-call]
        options.add_argument("--disable-dev-shm-usage")  # type: ignore[no-untyped-call]
        self._browser = selenium.webdriver.Chrome(options=options)
        self._root_url = root_url
        self._race_id = race_id
        self._max_wait = max_wait
        self._locked = False
        self._locked_page_source: str | None = None
        self._locked_page_soup: bs4.BeautifulSoup | None = None

    def lock(self) -> None:
        """Lock the browser on the current state of the web page."""
        assert not self._locked
        self._locked_page_source = self._browser.page_source
        self._locked_page_soup = bs4.BeautifulSoup(self._locked_page_source, "html.parser")
        self._locked = True

    def unlock(self) -> None:
        """Unlock the browser and follow new updates to the web page."""
        assert self._locked
        self._locked_page_source = None
        self._locked_page_soup = None
        self._locked = False

    @property
    def page_source(self) -> str:
        """Return the HTML source code of the current page."""
        if self._locked:
            assert self._locked_page_source is not None
            return self._locked_page_source
        else:
            return self._browser.page_source

    @property
    def page_soup(self) -> bs4.BeautifulSoup:
        """Return the HTML source code of the current page parse by BeautifulSoup."""
        if self._locked:
            assert self._locked_page_soup is not None
            return self._locked_page_soup
        else:
            return bs4.BeautifulSoup(self._browser.page_source, "html.parser")

    def ensure_locked(self) -> None:
        """Ensure that the browser is locked and, if not, raise an error."""
        if not self._locked:
            raise RuntimeError("Did you forget to lock the browser?")

    def ensure_unlocked(self) -> None:
        """Ensure that the browser is unlocked and, if not, raise an error."""
        if self._locked:
            raise RuntimeError("Did you forget to unlock the browser?")

    def get(self, url: str) -> None:
        """Load a web page in the current browser session."""
        self.ensure_unlocked()
        self._browser.get(url)

    def find_element(self, by: str, value: str) -> selenium.webdriver.remote.webelement.WebElement:
        """Find an element given a By strategy and locator."""
        self.ensure_unlocked()
        return self._browser.find_element(by, value)

    def find_elements(self, by: str, value: str) -> list[selenium.webdriver.remote.webelement.WebElement]:
        """Find an elements given a By strategy and locator."""
        self.ensure_unlocked()
        return self._browser.find_elements(by, value)

    def _wait_for_element(self, by: str, value: str) -> None:
        """Wait for an element to be present on the page."""
        self.ensure_unlocked()
        selenium.webdriver.support.wait.WebDriverWait(self._browser, self._max_wait).until(
            EC.presence_of_element_located((by, value)))  # type: ignore[no-untyped-call]

    def _wait_for_classification_timer(self, value: str) -> None:
        """Wait for classification timer to be greater than or equal to a certain value."""
        self.ensure_unlocked()

        def timer_above_value(
            locator: tuple[str, str]
        ) -> typing.Callable[[selenium.webdriver.remote.webdriver.WebDriver], bool]:
            """Predicate used in WebDriverWait, inspired by EC.text_to_be_present_in_element."""
            value_int = mathrace_interaction.time.convert_timestamp_to_number_of_seconds(value)

            def _predicate(driver: selenium.webdriver.remote.webdriver.WebDriver) -> bool:
                try:
                    element_text = driver.find_element(*locator).text
                    element_int = mathrace_interaction.time.convert_timestamp_to_number_of_seconds(element_text)
                    return element_int >= value_int
                except selenium.common.exceptions.StaleElementReferenceException:  # pragma: no cover
                    return False

            return _predicate

        selenium.webdriver.support.wait.WebDriverWait(self._browser, self._max_wait).until(
            timer_above_value((selenium.webdriver.common.by.By.ID, "orologio")))

    def _wait_for_classification_computed(self) -> None:
        """Wait for classification computation."""
        self.ensure_unlocked()
        selenium.webdriver.support.wait.WebDriverWait(self._browser, self._max_wait).until(
            JavascriptVariableEvaluatesToTrue("document.updated"))

    def login(self, username: str, password: str) -> None:
        """Log into the turing instance with the provided credentials."""
        self.get(urllib.parse.urljoin(self._root_url, "accounts/login"))
        # Wait for the login button to appear, and send credentials
        self._wait_for_element(selenium.webdriver.common.by.By.ID, "submit")
        self.find_element(selenium.webdriver.common.by.By.NAME, "username").send_keys(username)
        self.find_element(selenium.webdriver.common.by.By.NAME, "password").send_keys(password)
        self.find_element(selenium.webdriver.common.by.By.ID, "submit").click()
        # Successful login redirects to the home page, where there is a link to change password
        self._wait_for_element(selenium.webdriver.common.by.By.CSS_SELECTOR, "a[href='/accounts/password_change/']")

    def go_to_classification_page(self, classification_type: str, querystring: dict[str, str]) -> None:
        """Direct the browser to visit a specific classification type."""
        querystring_joined = (
            ("?" + "&".join(f"{k}={v}" for (k, v) in querystring.items())) if len(querystring) > 0 else "")
        self.get(
            urllib.parse.urljoin(
                self._root_url, f"engine/classifica/{self._race_id}/{classification_type}{querystring_joined}"))
        # Wait for the classification to be fully computed
        try:
            self._wait_for_classification_computed()
        except selenium.common.exceptions.TimeoutException:
            if "Purtroppo non sei autorizzato ad effettuare questa azione" in self.page_source:
                raise RuntimeError("The user does not have the permissions to see this classification")
            else:
                if len(self.find_elements(selenium.webdriver.common.by.By.NAME, "username")) > 0:
                    raise RuntimeError("The user must be logged in to see this classification")
                else:  # pragma: no cover
                    raise

    def ensure_classification_type(self, classification_type: str) -> None:
        """Ensure that the page contains a specific classification type."""
        expected_url = urllib.parse.urljoin(
            self._root_url, f"engine/classifica/{self._race_id}/{classification_type}")
        if not self._browser.current_url.startswith(expected_url):
            raise RuntimeError(f"The current page is not a {classification_type} classification")

    def get_teams_score(self) -> list[int]:
        """Get the score of the teams in the race."""
        self.ensure_locked()
        assert self._locked_page_soup is not None
        self.ensure_classification_type("squadre")
        team_id = 1
        scores = []
        while True:
            score_elements = self._locked_page_soup.find_all("span", id=f"label-points-{team_id}")
            if len(score_elements) == 0:
                break
            else:
                assert len(score_elements) == 1
                scores.append(int(score_elements[0].text))
                team_id += 1
        return scores

    def get_teams_position(self) -> list[int]:
        """Get the position of the teams in the race."""
        self.ensure_locked()
        assert self._locked_page_soup is not None
        self.ensure_classification_type("squadre")
        team_id = 1
        positions = []
        while True:
            position_elements = self._locked_page_soup.find_all("span", id=f"label-pos-{team_id}")
            if len(position_elements) == 0:
                break
            else:
                assert len(position_elements) == 1
                positions.append(int(position_elements[0].text[:-1]))  # :-1 is to drop the trailing degree symbol
                team_id += 1
        return positions

    def get_css_sources(self) -> dict[str, str]:
        """Get the content of CSS files used in the current page."""
        self.ensure_locked()
        assert self._locked_page_soup is not None
        all_css = dict()

        for css in self._locked_page_soup.find_all("link", rel="stylesheet"):
            # Do not use the current selenium browser to fetch the css content, otherwise
            # the browser would move away from the current page. However, since css content
            # is static, simply downloading the page via the python package requests suffices.
            response = requests.get(urllib.parse.urljoin(self._root_url, css["href"]))
            assert response.status_code == 200
            filename = css["href"].split("/")[-1]
            assert filename not in all_css, "Cannot have to css files with the same name"
            all_css[filename] = response.text

        return all_css

    def get_cleaned_html_source(self) -> str:
        """
        Get a cleaned HTML source code of a page of the turing instance for local download.

        The HTML code is preprocessed as follows:
            - the path of any css should be flattened to the one returned by get_css_sources.
            - any local link to the live instance is removed, since it would not be available locally.
            - any javascript is removed, since in order to be visible locally the page cannot contain
              any script that requires the live server.
        """
        self.ensure_locked()
        # Create a new soup object, because the existing one would be changed if we used it
        assert self._locked_page_source is not None
        soup = bs4.BeautifulSoup(self._locked_page_source, "html.parser")

        # Flatten css path
        for css in soup.find_all("link", rel="stylesheet"):
            css["href"] = css["href"].split("/")[-1]

        # Remove local links
        for a in soup.select("a[href]"):
            assert isinstance(a["href"], str)
            if a["href"].startswith("/"):
                del a["href"]

        # Remove <script> tags
        for script in soup.select("script"):
            script.decompose()

        # Return postprocessed page
        return str(soup)


class JavascriptVariableEvaluatesToTrue:
    """Helper class used to wait until a javascript variable is true."""

    def __init__(self, variable: str) -> None:
        self._variable = variable

    def __call__(self, driver: selenium.webdriver.remote.webdriver.WebDriver) -> bool:
        """Condition for waiting until the javascript variable is true."""
        return driver.execute_script(f"return {self._variable};")  # type: ignore[no-any-return, no-untyped-call]
