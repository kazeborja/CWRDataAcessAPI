from app.infrastructure.mongo_repos.generic_repository import GenericRepository
from commonworks.domain.models.work.work import Repository

__author__ = 'borja'


class WorkRepository(GenericRepository, Repository):
    def __init__(self, url_root):
        super(WorkRepository, self).__init__(url_root, 'works')

    def find_works_by_submitter(self, submitter_id):
        works = list(self._db[self.collection].find({'submitter_id': submitter_id}))

        if works is None:
            return "Work not found"

        return works

    def find_work_by_submitter_id(self, submitter_id, work_number):
        work = self._db[self.collection].find_one({'submitter_id': submitter_id, 'agreement_number': work_number})

        return work