
from chroma_db.chroma_db import ChromaDb
from pull_request.pull_request import PullRequest


class TestChromaDb():

    def test_chroma_db(self):
        chroma_db = ChromaDb()
        assert chroma_db.check_for_trigger('chromadb') == True

        assert chroma_db.call('chromadb') == 'chromadb'

class TestPullRequest():

    def test_pull_request(self):
        pull_request = PullRequest()
        assert pull_request.check_for_trigger('pull request') == True
        assert pull_request.check_for_trigger('pr#') == True
        assert pull_request.check_for_trigger('pull') == False

        assert pull_request.call('pull request') == None

        assert pull_request._extract_pull_request_number('pull request') == None