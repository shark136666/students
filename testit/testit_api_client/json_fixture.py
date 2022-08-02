class JSONFixture:
    @staticmethod
    def create_autotest(
        external_id,
        project_id,
        name,
        steps=None,
        setup=None,
        teardown=None,
        namespace=None,
        classname=None,
        title=None,
        description=None,
        links=None,
        labels=None
    ):
        json = {
            'externalId': external_id,
            'projectId': project_id,
            'name': name
        }

        if steps:
            json['steps'] = steps

        if setup:
            json['setup'] = setup

        if teardown:
            json['teardown'] = teardown

        if namespace:
            json['namespace'] = namespace

        if classname:
            json['classname'] = classname

        if title:
            json['title'] = title

        if description:
            json['description'] = description

        if links:
            json['links'] = links

        if labels:
            json['labels'] = labels

        return json

    @staticmethod
    def update_autotest(
        external_id,
        project_id,
        name,
        autotest_id,
        steps=None,
        setup=None,
        teardown=None,
        namespace=None,
        classname=None,
        title=None,
        description=None,
        links=None,
        labels=None
    ):
        json = {
            'externalId': external_id,
            'projectId': project_id,
            'name': name,
            'id': autotest_id
        }

        if steps:
            json['steps'] = steps

        if setup:
            json['setup'] = setup

        if teardown:
            json['teardown'] = teardown

        if namespace:
            json['namespace'] = namespace

        if classname:
            json['classname'] = classname

        if title:
            json['title'] = title

        if description:
            json['description'] = description

        if links:
            json['links'] = links

        if labels:
            json['labels'] = labels

        return json

    @staticmethod
    def create_testrun(project_id, name):
        return {
            'projectId': project_id,
            'name': name
        }

    @staticmethod
    def set_results_for_testrun(
        autotest_external_id,
        configuration_id,
        outcome,
        step_results=None,
        setup_results=None,
        teardown_results=None,
        traces=None,
        attachments=None,
        parameters=None,
        properties=None,
        links=None,
        duration=None,
        failure_reason_name=None,
        message=None
    ):
        json = {
            'autoTestExternalId': autotest_external_id,
            'configurationId': configuration_id,
            'outcome': outcome
        }

        if step_results:
            json['stepResults'] = step_results

        if setup_results:
            json['setupResults'] = setup_results

        if teardown_results:
            json['teardownResults'] = teardown_results

        if traces:
            json['traces'] = traces

        if attachments:
            json['attachments'] = attachments

        if parameters:
            json['parameters'] = parameters

        if properties:
            json['properties'] = properties

        if links:
            json['links'] = links

        if duration:
            json['duration'] = duration

        if failure_reason_name:
            json['failureReasonName'] = failure_reason_name

        if message:
            json['message'] = message

        return json
