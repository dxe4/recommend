import copy
import time
import sys
from functools import partial

import django
django.setup()

import requests
from django.conf import settings
from django.db.models import Count
from requests.auth import HTTPBasicAuth

from common.models import Repo, StargazerRepo, StargazerProfiles


auth = HTTPBasicAuth(settings.GH_USER, settings.GH_TOKEN)
authed_request = partial(requests.get, auth=auth)


class PaginatedRequest(object):

    def __init__(self, request_function, response_processor,
                 default_params=None, default_data=None, post_process_data=None):
        '''
        request_function: a function passed from the requests library
            this helps to use a functools.partial for authentication, so that
            you don't have to pass the credentials all the time
        response_processor: repsonse send to __call__
            before paginiation / rate limit is processed
        default_params: get parameters to be send to all requests
        default_data: post/patch etc data to be send on each request
        post_process_data: data to be passed to response_processor

        TODO change prints to logger.info
        '''
        self.request_function = request_function
        self.default_params = default_params or {}  # GET
        self.default_data = default_data or {}  # POST, PATCH etc
        self.response_processor = response_processor
        self.count = 0
        self.post_process_data = post_process_data

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
            time.sleep(int(wait_seconds) + 5)

    def process(self, url, params=None, data=None):
        # send request
        self.count += 1
        print("processing {}".format(self.count))
        request_data = self.request_data(params, data)
        response = self.request_function(
            url, data=request_data['data'], params=request_data['params']
        )
        # process request
        self.response_processor(response, post_process_data=self.post_process_data)

        # post process request
        self.wait_for_rate_limit(response.headers)

        link_header = response.links.get("next")
        if link_header:
            self.process(link_header['url'], params=params, data=data)


class MyStarsResponseProcessor(object):

    def __call__(self, response, post_process_data=None):
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
                stargazers_url=stargazers_url,
                stargazers_count=stargazers_count, full_name=full_name,
                description=description,
                username=settings.GH_USER
            )
            repositories.append(repo)

        Repo.objects.bulk_create(repositories)


class FetchStargazers(object):

    def __call__(self, response, post_process_data=None):
        stargazers = []
        repo_origin = post_process_data['repo_origin']
        data = response.json()

        for stargazer in data:
            username = stargazer['login']
            if username == settings.GH_USER:
                continue

            profile = StargazerProfiles(
                username=username,
                origin=repo_origin,
            )
            stargazers.append(profile)

        StargazerProfiles.objects.bulk_create(stargazers)


stargazers_params = {
    'visibility': 'public',
    'sort': 'created',
    'direction': 'desc',
}

def fetch_my_stars():

    url = 'https://api.github.com/user/starred'

    paginated_request = PaginatedRequest(
        authed_request, MyStarsResponseProcessor(),
        default_params=stargazers_params
    )
    paginated_request.process(url)

def repo_stargazers(url, repo_origin):
    paginated_request = PaginatedRequest(
        authed_request, FetchStargazers(),
        default_params=stargazers_params,
        post_process_data={'repo_origin': repo_origin}
    )
    paginated_request.process(url)


def fetch_stargazers():
    # for filter look into the model docs
    repositories = Repo.objects.filter(stargazers_count__lte=500)
    for repository in repositories:
        repo_stargazers(repository.stargazers_url, repository)

def most_relevant_profiles():
    # This doesn't imply anything, since some people have 30k stars..
    # probably filter anything > 2k
    most_relevant = StargazerProfiles.objects.all().values(
        'username'
    ).annotate(
        count=Count("username")
    ).order_by(
        "-count"
    )[0:10]
    print(most_relevant)


if __name__ == '__main__':
    funcs = {
        'my-stars': fetch_my_stars,
        'related-stargazers': fetch_stargazers,
        'most-relevant': most_relevant_profiles
    }
    try:
        funcs[sys.argv[1]]()
    except KeyError:
        print("possible options ", funcs.keys())
