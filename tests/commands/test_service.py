from re import match
from unittest import TestCase
from emcli.commands.service import ServiceCommand

class TestServiceCommandMethods(TestCase):
    
    def test_get_health_summary_healthy(self):
        (is_healthy, message) = ServiceCommand.get_health_summary('my-env', 'my-svc', 'blue', {
            'desiredCount': 1,
            'desiredAndHealthyCount': 1,
            'undesiredCount': 0
        })
        assert is_healthy == True
        assert message == 'the blue slice of my-svc in my-env is healthy'

    def test_get_health_summary_unhealthy(self):
        (is_healthy, message) = ServiceCommand.get_health_summary('my-env', 'my-svc', 'blue', {
            'desiredCount': 9,
            'desiredAndHealthyCount': 7,
            'undesiredCount': 0
        })
        assert is_healthy == False
        assert message == 'the blue slice of my-svc in my-env is not operating at capacity (7/9 healthy)'

    def test_get_health_summary_undesired(self):
        (is_healthy, message) = ServiceCommand.get_health_summary('my-env', 'my-svc', 'blue', {
            'desiredCount': 1,
            'desiredAndHealthyCount': 1,
            'undesiredCount': 1
        })
        assert is_healthy == True
        assert message == 'the blue slice of my-svc in my-env is healthy and may be routing requests to 1 unintended instance'

    def test_get_health_summary_unhealthy_and_undesired(self):
        (is_healthy, message) = ServiceCommand.get_health_summary('my-env', 'my-svc', 'blue', {
            'desiredCount': 3,
            'desiredAndHealthyCount': 1,
            'undesiredCount': 2
        })
        assert is_healthy == False
        assert message == 'the blue slice of my-svc in my-env may be routing requests to 2 unintended instances and is not operating at capacity (1/3 healthy)'
