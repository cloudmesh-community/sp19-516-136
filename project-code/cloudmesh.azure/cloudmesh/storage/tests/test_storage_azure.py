###############################################################
# pytest -v --capture=no tests/test_storage_azure.py
# pytest -v  tests/test_storage_azure.py
# pytest -v --capture=no tests/test_storage_azure.py:Test_storage.<METHODNAME>
###############################################################
import os
from pprint import pprint

from cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.variables import Variables
from cloudmesh.common.parameter import Parameter
import pytest
from cloudmesh.common.util import readfile
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import banner

#
# cms set storage=azure
#
@pytest.mark.incremental
class Test_storage:

    def create_dir(self, location):
        d = Path(os.path.dirname(path_expand(location)))
        d.mkdir(parents=True, exist_ok=True)

    def create_file(self, location, content):
        self.create_dir(location)
        writefile(path_expand(location), content)

    def setup(self):
        variables = Variables()
        self.service = Parameter.expand(variables['storage'])[0]
        self.p = Provider(service=self.service)
        self.sourcedir = os.path.expanduser("~/Documents/cloudmesh/storage/test")
        print()

    def test_create_source(self):
        HEADING()
        home = self.sourcedir
        # Setup a dir
        self.content = []
        self.files = ["a/a1.txt", "a/a2.txt", "a/a3.txt",
                  "a/b/b1.txt", "a/b/b2.txt", "a/b/b3.txt",
                  "a/b/c/c1.txt", "a/b/c/c2.txt", "a/b/c/c3.txt",
                  "a/b/d/d1.txt", "a/b/d/d2.txt", "a/b/d/d3.txt", "a/b/d/a1.txt"]

        for f in self.files:
            location = f"{home}/{f}"
            self.create_file(location, f"content of {f}")
            self.content.append(location)

        # setup empty dir in a
        d1 = Path(path_expand(f"{home}/a/empty"))
        d1.mkdir(parents=True, exist_ok=True)

        for f in self.files:
            assert os.path.isfile(f"{home}/{f}")

        assert os.path.isdir(f"{home}/a/empty")

    def test_put(self):
        HEADING()
        home = self.sourcedir
        local_path = f"{home}/a/a1.txt"
        cloud_path = "/"

        StopWatch.start("PUT file")
        test_file = self.p.put(local_path, cloud_path , False)
        StopWatch.stop("PUT file")

        assert test_file is not None

    def test_get(self):
        HEADING()
        home = self.sourcedir
        cloud_path = "/a1.txt"
        local_path = f"{home}/hello.txt"

        StopWatch.start("GET file")
        test_file = self.p.get(cloud_path, local_path, False)
        StopWatch.stop("GET file")

        assert test_file is not None

        content = readfile(local_path)
        assert "a1.txt" in content


    def test_list(self):
        HEADING()
        cloud_path = "/"

        StopWatch.start("LIST Directory")
        contents = self.p.list(cloud_path, False)
        StopWatch.stop("LIST Directory")

        for c in contents:
            pprint(c)

        assert len(contents) > 0
        found = False
        for entry in contents:
            if entry["cm"]["name"] == "a1.txt":
                found = True
        assert found

    def test_create_dir(self):
        HEADING()
        src = '/a/created_dir'
        StopWatch.start("CREATE DIR")
        directory = self.p.createdir(src)
        StopWatch.stop("CREATE DIR")
        pprint(directory)

        assert dir is not None
        assert "a/created_dir" in directory[0]["name"]

    def test_search(self):
        HEADING()
        src = '/'
        filename = "a1.txt"
        StopWatch.start("SEARCH file")
        search_files = self.p.search(src, filename, True)
        StopWatch.stop("SEARCH file")
        pprint(search_files)
        assert len(search_files) > 0
        assert search_files[0]["name"] == filename

    def test_delete(self):
        HEADING()
        src = "/a/created_dir"
        StopWatch.start("DELETE Directory")
        contents = self.p.delete(src)
        StopWatch.stop("DELETE Directory")
        deleted = False
        for entry in contents:
            if "created_dir" in entry["cm"]["name"]:
                if entry["cm"]["status"] == "deleted":
                    deleted = True
        assert deleted

    def test_recursive_put(self):
        # must be implemented by student from ~/.cloudmesh/storage/test
        # make sure all files are in the list see self.content which contains all files
        home = self.sourcedir
        StopWatch.start("PUT Directory --recursive")
        upl_files = self.p.put(f"{home}", "/a", True)
        StopWatch.stop("PUT Directory --recursive")
        pprint(upl_files)

        assert upl_files is not None

    def test_recursive_get(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/get
        # see self.content which contains all files but you must add get/
        home = self.sourcedir
        d2 = Path(path_expand(f"{home}/get"))
        d2.mkdir(parents=True, exist_ok=True)
        StopWatch.start("GET Directory --recursive")
        dnld_files = self.p.get("/a", f"{home}/get", True)
        StopWatch.stop("GET Directory --recursive")
        pprint(dnld_files)

        assert dnld_files is not None

    def test_recursive_delete(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/get
        # see self.content which contains all files but you must add get/
        src = "/a/a/b/c"
        StopWatch.start("DELETE Sub-directory")
        del_files = self.p.delete(src)
        StopWatch.stop("DELETE Sub-directory")

        assert len(del_files) > 0

    def test_exhaustive_list(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/
        # see self.content which contains all files that you can test against
        # in the list return. all of them must be in there
        StopWatch.start("LIST Directory --recursive")
        contents = self.p.list("/a", True)
        StopWatch.stop("LIST Directory --recursive")

        assert len(contents) > 0

    def test_selective_list(self):
        # must be implemented by student into ~/.cloudmesh/storage/test/a/b
        # see self.content which contains all files that you can test against
        # in the list return. all of them must be in there but not more?
        # I am unsure if we implemented a secive list. If not let us know
        # full list for now is fine
        StopWatch.start("LIST Sub-directory --recursive")
        contents = self.p.list("/a/a/b", True)
        StopWatch.stop("LIST Sub-directory --recursive")

        assert len(contents) > 0

    def test_search_b1(self):
        # search for b1.txt
        src = '/a'
        filename = 'b1.txt'
        StopWatch.start("SEARCH file --recursive")
        search_files = self.p.search(src, filename, True)
        StopWatch.stop("SEARCH file --recursive")

        assert search_files is not None

    def test_search_b1_dir(self):
        # search for b/b2.txt see that this one has even the dir in the search
        src = '/a'
        filename = '/b/b1.txt'
        StopWatch.start("SEARCH file under a sub-dir --r")
        search_files = self.p.search(src, filename, True)
        StopWatch.stop("SEARCH file under a sub-dir --r")
        assert search_files is not None

    def test_search_a1(self):
        # search for a1.txt which shold return 2 entries
        src = '/a'
        filename = 'a1.txt'
        StopWatch.start("SEARCH file under root dir --r")
        search_files = self.p.search(src, filename, True)
        StopWatch.stop("SEARCH file under root dir --r")

        assert len(search_files) == 2

    def test_results(self):
        HEADING()
        # storage = self.p.service
        service = self.service
        banner(f"Benchmark results for '{service}' Storage")
        StopWatch.benchmark()
