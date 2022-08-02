import mimetypes
import os
from ast import literal_eval
import requests


class Api(object):

    def __init__(self, url, private_token, proxy=None):
        self.url = url
        mimetypes.add_type('text/plain', '.log')
        self.request = requests.Session()
        self.request.headers = {'Authorization': 'PrivateToken ' + private_token}
        self.request.proxies = literal_eval(proxy) if proxy else {}

    # AutoTests
    def create_autotest(self, json):
        response = self.request.post(
            self.url + '/api/v2/autoTests',
            json=json
        )

        print(f"Autotest: {json['name']}")

        if response.status_code != 201:
            self.__exception(response, "Create autoTest")

        print('\nCreate autoTest passed!')

        return response.json()['id']

    def link_autotest(self, autotest_id, workitem_id):
        response = self.request.post(
            f'{self.url}/api/v2/autoTests/{autotest_id}/workItems',
            json={'id': workitem_id}
        )

        if response.status_code == 204:
            print('Link autoTest with workItems passed!')
        else:
            self.__exception(response, "Link autoTest with workItems", raise_true=False)

    def get_autotest(self, external_id, project_id):
        response = self.request.get(
            f'{self.url}/api/v2/autoTests?projectId={project_id}&externalId={external_id}'
        )

        if response.status_code != 200:
            self.__exception(response, "Get autoTest")

        print('\nGet autoTest passed!')

        return response

    def update_autotest(self, json):
        response = self.request.put(
            self.url + '/api/v2/autoTests',
            json=json
        )

        print(f"AutoTest: {json['name']}")

        if response.status_code != 204:
            self.__exception(response, "Update autoTest")

        print('Update autoTest passed!')

    # TestRuns
    def create_testrun(self, json):
        response = self.request.post(
            self.url + '/api/v2/testRuns',
            json=json
        )

        if response.status_code != 201:
            self.__exception(response, "Create testRun")

        print('Create testRun passed!')

        return response.json()['id']

    def get_testrun(self, testrun_id):
        response = self.request.get(
            f'{self.url}/api/v2/testRuns/{testrun_id}'
        )

        if response.status_code != 200:
            self.__exception(response, "Get testRun")

        print('Get testRun passed!')

        return response.json()['projectId'], response.json()['testResults']

    def set_results_for_testrun(self, testrun_id, json):
        response = self.request.post(
            f'{self.url}/api/v2/testRuns/{testrun_id}/testResults',
            json=json
        )

        if response.status_code != 200:
            self.__exception(response, "Set results")

        print('Set results passed!')

    def testrun_activity(self, testrun_id, action):
        response = self.request.post(
            f'{self.url}/api/v2/testRuns/{testrun_id}/{action}'
        )

        if response.status_code != 204:
            self.__exception(response, f"TestRun {action}")

        print(f'TestRun {action} passed!')

    def load_attachment(self, file):
        type_of_file = mimetypes.guess_type(file.name)[0]

        response = self.request.post(
            f'{self.url}/api/Attachments',
            files={
                'file': (os.path.basename(file.name),
                         file,
                         type_of_file if type_of_file else 'application/octet-stream')
            }
        )

        if response.status_code == 201:
            print(f'Attachment {file.name} loaded!')

            return response.json()['id']
        else:
            self.__exception(response, f"Attachment {file.name}", raise_true=False)

            return None

    # Helpers
    @staticmethod
    def __exception(response, method_name, raise_true=True):
        print(f"{method_name} status code: {response.status_code}")

        error_text = f"""{method_name} error: {
            response.json()['error']['key'] if 'error' in response.json()
                else response.json()['errors'] if 'errors' in response.json()
                      else response.json()}"""

        if raise_true:
            raise Exception(error_text)

        print(error_text)
    # Projects

    def get_project(self, projectName):
        response = self.request.get(
            f'{self.url}/api/v2/projects?projectName={projectName}'
        )

        if response.status_code != 200:
            self.__exception(response, "Get project")

        return response
    def get_workItems(self,projectId ):
        response = self.request.get(
            f'{self.url}/api/v2/projects/{projectId}/workItems'
        )

        if response.status_code != 200:
            self.__exception(response, "Get workItems")
        return response
