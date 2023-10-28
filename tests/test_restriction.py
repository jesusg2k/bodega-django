import pytest
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.firefox.options import Options
from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture(scope="class")
def setup(request):
    options = Options()
    #options.headless = True
    driver = webdriver.Firefox(options=options)
    request.cls.driver = driver
    yield driver
    #driver.close()



@pytest.mark.usefixtures('setup')
class TestUserLoginFormSuccess(LiveServerTestCase):
    def setUp(self):
        self.driver.get(self.live_server_url+'/register')
        self.user_email = self.driver.find_element(By.ID, 'id_email')
        self.user_pwd = self.driver.find_element(By.ID, 'first_password')
        self.user_repeat_pwd = self.driver.find_element(By.ID, 'second_password')
        self.user_username = self.driver.find_element(By.ID,'id_nombre_usuario')
        self.user_lastname = self.driver.find_element(By.ID, 'id_apellido')
        self.user_name = self.driver.find_element(By.ID, 'id_nombre')
        self.login = self.driver.find_element(By.ID, 'boton_registrar')

    def test_user_register_success(self):
        User.objects.create_user(username="PorfavorAnda", email="user_email_testing@gmail.com", password="PwdForTest1")
        self.user_email.send_keys("user_email_testing@gmail.com")
        self.user_pwd.send_keys("PwdForTest1")
        self.user_repeat_pwd.send_keys("PwdForTest1")
        self.user_name.send_keys("NombreTesting")
        self.user_lastname.send_keys("ApellidoTesting")
        self.user_username.send_keys("UsernameTesting")
        self.login.send_keys(Keys.ENTER)
        self.driver.implicitly_wait(30)
        self.project_redirect = self.driver.find_element(By.LINK_TEXT, 'Tipos de User Story')
        self.project_redirect.send_keys(Keys.ENTER)







