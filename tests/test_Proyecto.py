
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

from oauth_project.models.modelos import Proyecto


@pytest.fixture(scope="class")
def setup(request):
    options = Options()
    #options.headless = True
    driver = webdriver.Firefox(options=options)
    request.cls.driver = driver
    yield driver
    #driver.close()


@pytest.mark.xfail()
@pytest.mark.usefixtures('setup')
class TestUserLoginFormSuccess(LiveServerTestCase):
    def setUp(self):
        self.driver.get(self.live_server_url+'/misproyectos/crear-proyecto')
        self.driver.maximize_window()  # For maximizing window
        self.driver.implicitly_wait(5)  # gives an implicit wait for 20 seconds
        self.project_name = self.driver.find_element(By.NAME, 'data[nombre_proyecto]')
        self.project_description = self.driver.find_element(By.NAME, 'data[descripcion_proyecto]')
        self.project_scrumMaster = self.driver.find_element(By.NAME, 'data[scrum_master]')
        self.project_tipo_story = self.driver.find_element(By.NAME, 'data[datagrid_tipo_story][0][tipo_story-unique]')
        self.project_button = self.driver.find_element(By.NAME, 'data[submit]')



    def test_user_register_success(self):
        self.project_name.send_keys("Nombre")
        self.project_description.send_keys("Apellido")
        self.project_scrumMaster.send_keys(1)
        self.project_scrumMaster.send_keys(1)
        self.project_button.send_keys(Keys.ENTER)


        try:
            WebDriverWait(self.driver, 2) \
                .until(EC.url_matches(self.live_server_url + '/proyectos/'))
        except TimeoutException:
            print("Creacion del proyecto fallo")
        finally:
            self.assertURLEqual(self.driver.current_url, self.live_server_url + '/proyectos/')

















