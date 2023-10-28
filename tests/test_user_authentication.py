
import pytest
from django.contrib.auth.models import User
from django.contrib.gis.geos import factory
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.firefox.options import Options
from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from django.contrib.auth.hashers import make_password




@pytest.fixture(scope="class")
def setup(request):
    options = Options()
    #options.headless = True
    driver = webdriver.Firefox(options=options)
    request.cls.driver = driver
    yield driver
    #driver.close()




