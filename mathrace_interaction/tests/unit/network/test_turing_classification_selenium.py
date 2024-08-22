# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.network.TuringClassificationSelenium on mock web pages."""

import pytest
import pytest_httpserver
import selenium.webdriver.common.by
import selenium.webdriver.support.color

import mathrace_interaction.network
import mathrace_interaction.typing


class Browser(mathrace_interaction.network.TuringClassificationSelenium):
    """Helper class that extends TuringClassificationSelenium on the URL of the mock httpserver."""

    def __init__(self, httpserver: pytest_httpserver.HTTPServer) -> None:
        super().__init__(httpserver.url_for("/"), 0, 5)


def test_classification_browser_get(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.get."""
    httpserver.expect_request("/").respond_with_data("Hello world!", content_type="text/plain")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Hello world!" in browser.page_source


def test_classification_browser_get_locked(
    httpserver: pytest_httpserver.HTTPServer,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.get."""
    httpserver.expect_request("/").respond_with_data("Hello world!", content_type="text/plain")

    browser = Browser(httpserver)
    browser.lock()
    runtime_error_contains(lambda: browser.get(httpserver.url_for("/")), "Did you forget to unlock the browser?")


def test_classification_browser_lock_unlock_content(
    httpserver: pytest_httpserver.HTTPServer,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test interaction of page content with mathrace_interaction.network.TuringClassificationSelenium.lock/unlock."""
    javascript_button_page = """<html>
<body>
<script>
function incrementTime() {
    const prefix = "Current time is ";
    var current_time = parseInt(document.getElementById("time").textContent.replace(prefix, ""));
    document.getElementById("time").textContent = prefix + (current_time + 1).toString();
}
</script>
<span id="time">Current time is 0</span>
<button id="increment" onclick="incrementTime()">Increment time</button>
</body>
</html>"""
    httpserver.expect_request("/").respond_with_data(javascript_button_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Current time is 0" in browser.page_source

    # Now lock the page, click on the button and verify that the content seen by browser is unchanged,
    # yet the content on the actual selenium object did change
    # Note that we need to find the button before locking, otherwise the find_element method throws
    # a runtime error
    increment_button = browser.find_element(selenium.webdriver.common.by.By.ID, "increment")
    browser.lock()
    runtime_error_contains(
        lambda: browser.find_element(selenium.webdriver.common.by.By.ID, "increment"),
        "Did you forget to unlock the browser?")
    increment_button.click()
    assert "Current time is 0" in browser.page_source
    assert "Current time is 1" in browser._browser.page_source
    assert "Current time is 0" in browser.page_soup.find_all("span")[0].text

    # Now unlock the page, and check that the content seen by the browser is updated.
    browser.unlock()
    assert "Current time is 1" in browser.page_source
    assert "Current time is 1" in browser._browser.page_source
    assert "Current time is 1" in browser.page_soup.find_all("span")[0].text


def test_classification_browser_login(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.login."""
    login_page = f"""<html>
<body>
<form action="{httpserver.url_for("/engine")}">
    <input type="text" name="username">
    <input type="password" name="password">
    <input type="submit" id="submit" value="Login">
</form>
</body>
</html>"""
    post_login_page = """<html>
<body>
<span id="qs">Processing querystring</span>
<script>
const params = new URLSearchParams(window.location.search);
document.getElementById("qs").textContent =
    "username is " + params.get("username") + " and password is " + params.get("password");
</script>
<a href="/accounts/password_change/">Cambio password</a>
</body>
</html>"""
    httpserver.expect_request("/accounts/login").respond_with_data(login_page, content_type="text/html")
    httpserver.expect_request("/engine").respond_with_data(post_login_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.login("admin", "secret")
    assert "Processing querystring" not in browser.page_source
    assert "username is admin and password is secret" in browser.page_source
    assert "Cambio password" in browser.page_source


def test_classification_browser_go_to_classification_page(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.go_to_classification_page."""
    classification_page = """<html>
<body>
<span id="qs">Processing classification</span>
<script>
document.updated = false;
setTimeout(function(){
    document.getElementById("qs").textContent = "Classification has " + "been computed";
    document.updated = true;
}, 10);
</script>
</body>
</html>"""
    httpserver.expect_request("/engine/classifica/0/unica").respond_with_data(
        classification_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.go_to_classification_page("unica", {})
    assert "Processing classification" not in browser.page_source
    assert "Classification has been computed" in browser.page_source


@pytest.mark.parametrize("page_content,expected_error", [
    (
        "Purtroppo non sei autorizzato ad effettuare questa azione",
        "The user does not have the permissions to see this classification"
    ),
    (
        '<input type="text" name="username">',
        "The user must be logged in to see this classification"
    )
])
def test_classification_browser_go_to_classification_page_error(
    httpserver: pytest_httpserver.HTTPServer, page_content: str, expected_error: str,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.go_to_classification_page raises errors."""
    classification_page = f"""<html>
<body>
{page_content}
</body>
</html>"""
    httpserver.expect_request("/engine/classifica/0/unica").respond_with_data(
        classification_page, content_type="text/html")

    browser = Browser(httpserver)
    runtime_error_contains(lambda: browser.go_to_classification_page("unica", {}), expected_error)


@pytest.mark.parametrize("query", ["score", "position"])
@pytest.mark.parametrize("querystring", [{}, {"initial_1": "0", "initial_2": "1", "initial_3": "2"}])
def test_classification_browser_get_teams_score_position(
    httpserver: pytest_httpserver.HTTPServer, query: str, querystring: dict[str, str],
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.get_teams_score/get_teams_position."""
    if query == "score":
        label = "points"
        extra_char = ""

        def query_function(browser: Browser) -> list[int]:
            """Get the score of the teams in the race."""
            return browser.get_teams_score()
    else:
        assert query == "position"
        label = "pos"
        extra_char = "*"

        def query_function(browser: Browser) -> list[int]:
            """Get the position of the teams in the race."""
            return browser.get_teams_position()

    classification_page = """<html>
<body>
<script>"""

    if len(querystring) == 0:
        classification_page +="""
const initial_1 = 0;
const initial_2 = 1;
const initial_3 = 2;"""
    else:
        classification_page +="""
const params = new URLSearchParams(window.location.search);
const initial_1 = parseInt(params.get("initial_1"));
const initial_2 = parseInt(params.get("initial_2"));
const initial_3 = parseInt(params.get("initial_3"));"""

    classification_page += """
document.updated = false;
setTimeout(function(){
    document.getElementById("LABEL-1").textContent = initial_1.toString() + "EXTRA_CHAR";
    document.getElementById("LABEL-2").textContent = initial_2.toString() + "EXTRA_CHAR";
    document.getElementById("LABEL-3").textContent = initial_3.toString() + "EXTRA_CHAR";
    document.updated = true;
}, 10);

var current_time = 0;
function incrementLabel() {
    current_time += 1;
    document.getElementById("LABEL-1").textContent = (initial_1 + current_time).toString() + "EXTRA_CHAR";
    document.getElementById("LABEL-2").textContent = (initial_2 + current_time * 2).toString() + "EXTRA_CHAR";
    document.getElementById("LABEL-3").textContent = (initial_3 + current_time * 3).toString() + "EXTRA_CHAR";
}
</script>
Team 1: <span id="LABEL-1"></span>
Team 2: <span id="LABEL-2"></span>
Team 3: <span id="LABEL-3"></span>
<button id="increment" onclick="incrementLabel()">Increment labels</button>
</body>
</html>""".replace(  # cannot use f-string directly because javascript has { ... }
    "LABEL", f"label-{label}").replace("EXTRA_CHAR", extra_char)
    httpserver.expect_request("/engine/classifica/0/squadre").respond_with_data(
        classification_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.go_to_classification_page("squadre", querystring)
    assert f'Team 1: <span id="label-{label}-1">0{extra_char}</span>' in browser.page_source
    assert f'Team 2: <span id="label-{label}-2">1{extra_char}</span>' in browser.page_source
    assert f'Team 3: <span id="label-{label}-3">2{extra_char}</span>' in browser.page_source

    # Click on the button once to check that it works correctly
    increment_button = browser.find_element(selenium.webdriver.common.by.By.ID, "increment")
    increment_button.click()
    assert f'Team 1: <span id="label-{label}-1">1{extra_char}</span>' in browser.page_source
    assert f'Team 2: <span id="label-{label}-2">3{extra_char}</span>' in browser.page_source
    assert f'Team 3: <span id="label-{label}-3">5{extra_char}</span>' in browser.page_source

    # The browser needs to be locked to proceed with the computation
    runtime_error_contains(lambda: query_function(browser), "Did you forget to lock the browser?")

    # Get the computed values, and compare them with the expected ones
    browser.lock()
    computed = query_function(browser)
    assert computed == [1, 3, 5]

    # Increment again the labels
    increment_button.click()

    # The source seen by the browser does not get updated until the browser is unlocked
    assert f'Team 1: <span id="label-{label}-1">1{extra_char}</span>' in browser.page_source
    assert f'Team 2: <span id="label-{label}-2">3{extra_char}</span>' in browser.page_source
    assert f'Team 3: <span id="label-{label}-3">5{extra_char}</span>' in browser.page_source
    browser.unlock()
    assert f'Team 1: <span id="label-{label}-1">2{extra_char}</span>' in browser.page_source
    assert f'Team 2: <span id="label-{label}-2">5{extra_char}</span>' in browser.page_source
    assert f'Team 3: <span id="label-{label}-3">8{extra_char}</span>' in browser.page_source

    # Get the computed values, and compare them with the expected ones
    browser.lock()
    computed = query_function(browser)
    assert computed == [2, 5, 8]


@pytest.mark.parametrize("query", ["score", "position"])
def test_classification_browser_get_teams_score_position_wrong_classification_type(
    httpserver: pytest_httpserver.HTTPServer, query: str,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test that error is raised when trying to query for teams score/position on an unsupported classification."""
    if query == "score":
        def query_function(browser: Browser) -> list[int]:
            """Get the score of the teams in the race."""
            return browser.get_teams_score()
    else:
        assert query == "position"

        def query_function(browser: Browser) -> list[int]:
            """Get the position of the teams in the race."""
            return browser.get_teams_position()

    classification_page = """<html>
<body>
<script>
document.updated = false;
setTimeout(function(){
    document.updated = true;
}, 10);
</script>
</body>
</html>"""
    httpserver.expect_request("/engine/classifica/0/unica").respond_with_data(
        classification_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.go_to_classification_page("unica", {})

    browser.lock()
    runtime_error_contains(lambda: query_function(browser), "The current page is not a squadre classification")


def test_classification_browser_get_css_sources(
    httpserver: pytest_httpserver.HTTPServer,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium.get_css_sources."""
    index_page = """<html>
<head>
    <link href="/folder1/style1.css" rel="stylesheet" type="text/css">
    <link href="/folder2/subfolder2/style2.css" rel="stylesheet" type="text/css">
</head>
<body>
<div id="container"><span id="text">Hello world!</span></div>
</body>
</html>"""
    style1_css = """div {
  background-color: #ff0000;
}"""
    style2_css = """span {
  color: #00ffff;
}"""

    httpserver.expect_request("/").respond_with_data(index_page, content_type="text/html")
    httpserver.expect_request("/folder1/style1.css").respond_with_data(style1_css, content_type="text/css")
    httpserver.expect_request("/folder2/subfolder2/style2.css").respond_with_data(style2_css, content_type="text/css")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Hello world!" in browser.page_source

    # Ensure that background color and text color are as expected
    container = browser.find_element(selenium.webdriver.common.by.By.ID, "container")
    bg_color_rgba = container.value_of_css_property("background-color")
    assert selenium.webdriver.support.color.Color.from_string(bg_color_rgba).hex == "#ff0000"
    text = browser.find_element(selenium.webdriver.common.by.By.ID, "text")
    color_rgba = text.value_of_css_property("color")
    assert selenium.webdriver.support.color.Color.from_string(color_rgba).hex == "#00ffff"

    # Get a dictionary containing the sources of all CSS files
    browser.lock()
    all_css = browser.get_css_sources()
    assert len(all_css) == 2
    assert "style1.css" in all_css
    assert "style2.css" in all_css
    assert all_css["style1.css"] == style1_css
    assert all_css["style2.css"] == style2_css


def test_classification_browser_get_cleaned_html_source_replaces_css(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test cleaning HTML source replaces css file names."""
    index_page = """<html>
<head>
    <link href="/folder1/style1.css" rel="stylesheet" type="text/css">
    <link href="/folder2/subfolder2/style2.css" rel="stylesheet" type="text/css">
</head>
<body>
<div id="container"><span id="text">Hello world!</span></div>
</body>
</html>"""
    style1_css = """div {
  background-color: #ff0000;
}"""
    style2_css = """span {
  color: #00ffff;
}"""

    httpserver.expect_request("/").respond_with_data(index_page, content_type="text/html")
    httpserver.expect_request("/folder1/style1.css").respond_with_data(style1_css, content_type="text/css")
    httpserver.expect_request("/folder2/subfolder2/style2.css").respond_with_data(style2_css, content_type="text/css")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Hello world!" in browser.page_source
    assert '"/folder1/style1.css"' in browser.page_source
    assert '"/folder2/subfolder2/style2.css"' in browser.page_source

    # Get the postprocessed HTML source, and check that it contains the flattened css names
    browser.lock()
    postprocessed_source = browser.get_cleaned_html_source()
    assert '"style1.css"' in postprocessed_source
    assert '"style2.css"' in postprocessed_source
    assert '"/folder1/style1.css"' not in postprocessed_source
    assert '"/folder2/subfolder2/style2.css"' not in postprocessed_source
    browser.unlock()

    # Ensure that background color and text color are as expected, i.e. changing the file names
    # in the postprocessed source did not affect the live page.
    container = browser.find_element(selenium.webdriver.common.by.By.ID, "container")
    bg_color_rgba = container.value_of_css_property("background-color")
    assert selenium.webdriver.support.color.Color.from_string(bg_color_rgba).hex == "#ff0000"
    text = browser.find_element(selenium.webdriver.common.by.By.ID, "text")
    color_rgba = text.value_of_css_property("color")
    assert selenium.webdriver.support.color.Color.from_string(color_rgba).hex == "#00ffff"


def test_classification_browser_get_cleaned_html_source_strips_links(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test that cleaning HTML sources strips links from output."""
    start_page = """<html>
<body>
<a href="/redirect" id="link">Redirect</a>
</body>
</html>"""
    redirect_page = """<html>
<body>
Success!
</body>
</html>"""
    httpserver.expect_request("/").respond_with_data(start_page, content_type="text/html")
    httpserver.expect_request("/redirect").respond_with_data(redirect_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Redirect" in browser.page_source
    assert "/redirect" in browser.page_source
    assert "<a href" in browser.page_source

    # Get the postprocessed HTML source, and check that it does not have any href attribute
    browser.lock()
    postprocessed_source = browser.get_cleaned_html_source()
    assert "Redirect" in postprocessed_source
    assert "/redirect" not in postprocessed_source
    assert "<a " in postprocessed_source
    assert "href" not in postprocessed_source
    browser.unlock()

    # Click on the link to check that it works, i.e. removing the href
    # from the postprocessed source did not affect the live page.
    browser.find_element(selenium.webdriver.common.by.By.ID, "link").click()
    assert "Success!" in browser.page_source


def test_classification_browser_get_cleaned_html_source_strips_javascript(
    httpserver: pytest_httpserver.HTTPServer
) -> None:
    """Test that cleaning HTML sources strips javascript from output."""
    javascript_button_page = """<html>
<body>
<script>
function incrementTime() {
    const prefix = "Current time is ";
    var current_time = parseInt(document.getElementById("time").textContent.replace(prefix, ""));
    document.getElementById("time").textContent = prefix + (current_time + 1).toString();
}
</script>
<span id="time">Current time is 0</span>
<button id="increment" onclick="incrementTime()">Increment time</button>
</body>
</html>"""
    httpserver.expect_request("/").respond_with_data(javascript_button_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.get(httpserver.url_for("/"))
    assert "Current time is 0" in browser.page_source
    assert "<script>" in browser.page_source

    # Click on the button once to check that it works correctly
    increment_button = browser.find_element(selenium.webdriver.common.by.By.ID, "increment")
    increment_button.click()
    assert "Current time is 0" not in browser.page_source
    assert "Current time is 1" in browser.page_source
    assert "<script>" in browser.page_source

    # Get the postprocessed HTML source, and check that it does not have any <script> tag
    browser.lock()
    postprocessed_source = browser.get_cleaned_html_source()
    assert "Current time is 1" in postprocessed_source
    assert "<script>" not in postprocessed_source
    browser.unlock()

    # Click on the button again to check that it still works, i.e. removing the <script>
    # tag from the postprocessed source did not affect the live page.
    increment_button.click()
    assert "Current time is 0" not in browser.page_source
    assert "Current time is 1" not in browser.page_source
    assert "Current time is 2" in browser.page_source
    assert "<script>" in browser.page_source


def test_classification_browser_wait_for_classification_timer(httpserver: pytest_httpserver.HTTPServer) -> None:
    """Test mathrace_interaction.network.TuringClassificationSelenium._wait_for_classification_timer."""
    classification_page = """<html>
<body>
<script>
document.updated = false;
setTimeout(function(){
    document.updated = true;
}, 10);
setTimeout(function(){
    document.getElementById("orologio").textContent = "00:00:0" + "1";
}, 1000);
</script>
<span id="orologio">00:00:00</span>
</html>"""
    httpserver.expect_request("/engine/classifica/0/unica").respond_with_data(
        classification_page, content_type="text/html")

    browser = Browser(httpserver)
    browser.go_to_classification_page("unica", {})
    assert "00:00:00" in browser.page_source
    assert "00:00:01" not in browser.page_source

    browser._wait_for_classification_timer("00:00:01")
    assert "00:00:00" not in browser.page_source
    assert "00:00:01" in browser.page_source
