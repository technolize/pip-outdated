import pkg_resources
try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib
import pip
import pip.download
from pip.log import logger
from pip.basecommand import Command
from pip.util import get_installed_distributions
from pip.commands.search import transform_hits, compare_versions, highest_version

index_url = 'http://pypi.python.org/pypi'

class OutdatedCommand(Command):
    name = 'outdated'
    usage = '%prog'
    summary = 'Display all packages that need updates'

    def __init__(self, *args, **kw):
        super(OutdatedCommand, self).__init__(*args, **kw)
    
    def run(self, options, args):
        self.installed_packages = [p.project_name for p in pkg_resources.working_set]
        self.pypi = xmlrpclib.ServerProxy(index_url, pip.download.xmlrpclib_transport)
        packages = set([])
        for dist in get_installed_distributions(local_only=True):
            pypi_hits = self.search(dist.key)
            hits = transform_hits(pypi_hits)
            data = [(i['name'], highest_version(i['versions'])) for i in hits]
            packages = packages.union(set(data))
        self.print_results(packages)
    
    def search(self, query):
        hits = self.pypi.search({'name': query})
        return hits
    
    def print_results(self, hits):
        for hit in hits:
            name, latest = hit
            if not name in self.installed_packages:
                continue
            dist = pkg_resources.get_distribution(name)
            if dist.version < latest:
                try:
                    logger.notify('{0} ({1} < {2})'.format(name, dist.version, latest))
                except UnicodeEncodeError:
                    pass
