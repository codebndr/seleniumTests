from codebender_testing.utils import SeleniumTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from codebender_testing import config
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pytest


class TestSketchesCounters(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        pass

    def test_sketches_counters(self):
        driver = self.driver
        # Check that the counters: Public sketches (blue) and Private sketches
        # (purple) have the correct value (number of sketches of each category).

        assert self.get_element(By.ID, "private-sketches-counter").text=="0"
        assert self.get_element(By.ID,"public-sketches-counter").text=="0"

        # Check that the counter for private projects also appears at the Badges
        # section and has the correct value.
        privateProjects = self.get_element(By.ID,
            "available-private-sketches-counter").text
        assert self.get_element(By.ID,
            "privateProjectAvailableNumber").text == \
            privateProjects.split('/')[0]

        # Check that the counter for available private sketches also appears at
        # the upload sketch modal (ino, zip, multiple zip) and at the create and
        # edit sketch modal.

        # Upload .ino.
        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-ino").click()
        assert self.get_element(By.ID,
            "upload-sketch-modal-available-private-sketches").text == \
            privateProjects
        close_btn = self.get_element(By.CSS_SELECTOR,
            "#home-upload-sketch-modal .btn-danger")
        close_btn.click()
        # Wait for the modal to close.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".modal-backdrop fade")
            )
        )

        # Upload .zip.
        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-zip").click()
        assert self.get_element(By.ID,
            "upload-sketch-modal-available-private-sketches").text == \
            privateProjects
        close_btn = self.get_element(By.CSS_SELECTOR,
            "#home-upload-sketch-modal .btn-danger")
        close_btn.click()
        # Wait for the modal to close.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".modal-backdrop fade")
            )
        )

        # Upload your sketch folder [.zip].
        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-folder-zip").click()
        assert self.get_element(By.ID,
            "upload-sketch-modal-available-private-sketches").text == \
            privateProjects
        close_btn = self.get_element(By.CSS_SELECTOR,
            "#home-upload-sketch-modal .btn-danger")
        close_btn.click()
        # Wait for the modal to close.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".modal-backdrop fade")
            )
        )

        # Create sketch modal.
        self.get_element(By.ID, "create_sketch_btn").click()
        assert self.get_element(By.ID,
            "create-sketch-modal-available-private-sketches").text == \
            privateProjects
        close_btn = self.get_element(By.CSS_SELECTOR,
            "#create-sketch-modal .btn-danger")
        close_btn.click()
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".modal-backdrop fade")
            )
        )

        # Create one public project.
        self.create_sketch('public' , 'publicSketch1', 'short description')
        self.open("/")

        # Check that public sketch number was increased from 0 to 1.
        assert self.get_element(By.ID, "public-sketches-counter").text=="1"

        # Create one private project.
        self.create_sketch('private' , 'privateSketch1', 'short description')
        self.open("/")

        # Check that private sketch number was increased from 0 to 1.
        assert self.get_element(By.ID, "private-sketches-counter").text=="1"

        # Check that the counter for available private projects that appears at
        # the Badges section has the correct value.

        private_sketches = self.get_element(By.ID,
            "available-private-sketches-counter").text
        assert self.get_element(By.ID,
            "privateProjectAvailableNumber").text == \
            private_sketches.split('/')[0]

        # Check that the number of private and public projects is updated
        # each time that you make a change (change a sketch from public
        # to private and vice versa).
        editInfo = driver.find_element_by_css_selector(
            '#project_list li[data-name="publicSketch1"] \
            .sketch-block-container .sketch-block-header \
            .sketch-block-edit-info')
        hoverEditInfo = ActionChains(driver).move_to_element(editInfo).perform()
        editInfoClick =  driver.find_element_by_css_selector(
            '#project_list li[data-name="publicSketch1"] \
            .sketch-block-container .sketch-block-header \
            .sketch-block-edit-info a')
        editInfoClick.click()
        # Change project from public to private.
        privateRadioButton = self.get_element(By.CSS_SELECTOR,
            '#edit-sketch-modal-type-controls [value="private"]')
        privateRadioButton.click()
        # Click the Save button.
        save_btn = self.get_element(By.CSS_SELECTOR,
            "#edit-sketch-modal .btn-success")
        save_btn.click()
        # Wait for the modal to close.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, "#edit-sketch-modal")
            )
        )
        # Check public and private projects counters.
        assert self.get_element(By.ID, "private-sketches-counter").text=="2"
        assert self.get_element(By.ID, "public-sketches-counter").text=="0"

        editInfo = driver.find_element_by_css_selector(
            '#project_list li[data-name="publicSketch1"] \
            .sketch-block-container .sketch-block-header \
            .sketch-block-edit-info')
        hoverEditInfo = ActionChains(driver).move_to_element(editInfo).perform()
        editInfoClick =  driver.find_element_by_css_selector(
            '#project_list li[data-name="publicSketch1"] \
            .sketch-block-container .sketch-block-header \
            .sketch-block-edit-info a')
        editInfoClick.click()
        # Change project from private to public.
        publicRadioButton = self.get_element(By.CSS_SELECTOR,
            '#edit-sketch-modal-type-controls [value="public"]')
        publicRadioButton.click()
        # Click the Save button.
        save_btn = self.get_element(By.CSS_SELECTOR,
            "#edit-sketch-modal .btn-success")
        save_btn.click()
        # Wait for the modal to close.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, "#edit-sketch-modal")
            )
        )
        # Check public and private projects counters.
        assert self.get_element(By.ID, "private-sketches-counter").text=="1"
        assert self.get_element(By.ID, "public-sketches-counter").text=="1"


    def test_sketch_filters(self):
        # Check that All, Public and Private buttons work, by clicking on each
        # of them and verifying hat the correct number of sketches appears.

        # Check "All sketches button".
        self.get_element(By.CSS_SELECTOR,
            '#filter-options label[data-filter="all"]').click()
        sketches = self.find_all('#project_list >li')
        assert len(sketches) == 2

        # Check "Public button".
        self.get_element(By.CSS_SELECTOR,
            '#filter-options label[data-filter="public"]').click()
        sketches = self.find_all('#project_list >li .cb-icon-globe-inv')
        assert len(sketches) == 1

        # Check "Private button".
        self.get_element(By.CSS_SELECTOR,
            '#filter-options label[data-filter="private"]').click()
        sketches = self.find_all('#project_list >li .fa-lock')
        assert len(sketches) == 1

class TestDeleteAllSketches(SeleniumTestCase):

    def test_delete(self, tester_login):
        try:
            sketches = self.find_all('#project_list > li \
                .sketch-block-title > a')
            projects = []
            for sketch in sketches:
                projects.append(sketch.text)
            for project in projects:
                self.delete_project(project)
        except:
            print 'No sketches found'

        self.logout()
