from testit_api_client.api import Api
from testit_api_client.json_fixture import JSONFixture
import json
url="http://192.168.9.94"
private_token = "Rjd5cXhFZmJXN3JGYXk0SjRE"
requests = Api(url, private_token)
project_id = 'd3157c19-2e68-44f8-ac50-301831ff949b'
testrun_name= 'kek'






project = requests.get_project("snvna")
project_id= json.loads(project.text)[0]["id"]
test = requests.get_workItems(project_id)
test = json.loads(test.text)
print(project_id)
print(test[0])
