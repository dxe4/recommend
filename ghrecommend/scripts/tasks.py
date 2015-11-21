import copy
import time
from functools import partial

import django
django.setup()

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from common.models import Repo


auth = HTTPBasicAuth(settings.GH_USER, settings.GH_TOKEN)
authed_request = partial(requests.get, auth=auth)


class PaginatedRequest(object):

    def __init__(self, request_function, response_processor, default_params=None, default_data=None):
        '''
        request_function: a function passed from the requests library
            this helps to use a functools.partial for authentication, so that
            you don't have to pass the credentials all the time
        response_processor: repsonse send to __call__
            before paginiation / rate limit is processed
        default_params: get parameters to be send to all requests
        default_data: post/patch etc data to be send on each request

        TODO change prints to logger.info
        '''
        self.request_function = request_function
        self.default_params = default_params or {}  # GET
        self.default_data = default_data or {}  # POST, PATCH etc
        self.response_processor = response_processor
        self.count = 0

    def request_data(self, params, data):
        default_params = copy.copy(self.default_params)
        default_data = copy.copy(self.default_data)

        if params:
            default_params.update(params)

        if data:
            default_data.update(data)

        return {
            'params': default_params,
            'data': default_data,
        }

    def wait_for_rate_limit(self, response_headers):
        rate_limit_remaining = response_headers.get('X-RateLimit-Remaining')
        rate_limit_reset = response_headers.get('X-RateLimit-Reset')

        if rate_limit_remaining is not None and rate_limit_remaining <= 2:
            wait_seconds = rate_limit_reset - time.time()
            print("waiting for {} s".format(wait_seconds))
            time.sleep(wait_seconds)

    def process(self, url, params=None, data=None):
        # send request
        self.count += 1
        print("processing {}".format(self.count))
        request_data = self.request_data(params, data)
        response = self.request_function(
            url, data=request_data['data'], params=request_data['params']
        )
        # process request
        self.response_processor(response)

        # post process request
        self.wait_for_rate_limit(response.headers)

        link_header = response.links.get("next")
        if link_header:
            self.process(link_header['url'], params=params, data=data)


class MyStarsResponseProcessor(object):

    def __call__(self, response):
        repositories = []
        data = response.json()

        for repository in data:
            if repository.get("private"):
                continue

            stargazers_url = repository['stargazers_url']
            stargazers_count = repository['stargazers_count']
            full_name = repository['full_name']
            description = repository.get("description")

            repo = Repo(
                stargazers_url=stargazers_url, stargazers_count=stargazers_count,
                full_name=full_name, description=description, username=settings.GH_USER
            )
            repositories.append(repo)

        Repo.objects.bulk_create(repositories)


if __name__ == '__main__':
    params = {
        'visibility': 'public',
        'sort': 'created',
        'direction': 'desc',
    }
    url = 'https://api.github.com/user/starred'

    paginated_request = PaginatedRequest(
        authed_request, MyStarsResponseProcessor(), default_params=params
    )
    paginated_request.process(url)
