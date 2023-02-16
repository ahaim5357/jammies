import os
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Any, Set
import re
import requests
from mimetypes import guess_extension
from uuid import uuid4
from zipfile import ZipFile
from io import BytesIO
from git import Repo
import json

# TODO: document
JsonObject = Dict[str, Any]

# Project file abstract information
# TODO: document
class ProjectFile(ABC):

    # TODO: Document
    def __init__(self, dir: str = os.curdir) -> None:
        super().__init__()
        self.dir: str = dir

    # TODO: Document
    @abstractmethod
    def setup(self, out_dir: str) -> bool:
        out_dir = out_dir if self.dir == os.curdir else self._get_path(out_dir)
        os.makedirs(out_dir, exist_ok = True)
        return False

    # TODO: Document
    @abstractmethod
    def file_type(self) -> str:
        pass

    # TODO: Document
    @abstractmethod
    def to_json(self) -> JsonObject:
        obj: JsonObject = {}
        obj['type'] = self.file_type()
        if self.dir != os.curdir:
            obj['dir'] = self.dir
        return obj

    # TODO: Document
    def _get_path(self, out_dir: str, *paths: str) -> str:
        fpath: List[str] = [out_dir, self.dir]
        fpath += paths
        return os.sep.join(fpath)

    # TODO: Document
    __filename_regex: str = r'filename=\"([^\"]+)\"'
    __content_disposition: str = 'content-disposition'
    __content_type: str = 'content-type'

    # TODO: Document
    @classmethod
    def _download_file(cls, url: str, handler: Callable[[requests.Response, str], bool]) -> bool:

        # Download data
        with requests.get(url, stream = True, allow_redirects = True) as response: # type: requests.Response
            # Return failure on download if cannot grab
            if not response.ok:
                return False
            
            # Get filename
            filename: Optional[str] = None
            
            # If the content disposition exists, then look up filename
            if cls.__content_disposition in response.headers:
                filename_lookup: Optional[re.Match[str]] = re.search(cls.__filename_regex, response.headers[cls.__content_disposition])
                if filename_lookup is not None:
                    filename: str = filename_lookup[1]
            
            # If the filename wasn't available, generate default name
            if filename is None:
                filename: str = str(uuid4())
                # Set content type, if available
                if cls.__content_type in response.headers:
                    filename += guess_extension(response.headers[cls.__content_disposition].partition(';')[0].strip())

            return handler(response, filename)
            
# OSF project file
# TODO: document
class OSFProjectFile(ProjectFile):

    # TODO: Document
    def __init__(self, id: str, dir: str = os.curdir) -> None:
        super().__init__(dir)
        self.id: str = id
        self.url: str = f'https://files.osf.io/v1/resources/{id}/providers/osfstorage/?zip='

    def file_type(self) -> str:
        return 'osf'

    def to_json(self) -> JsonObject:
        obj: JsonObject = super().to_json()
        obj['id'] = self.id
        return obj

    def setup(self, out_dir: str) -> bool:
        super().setup(out_dir)
        return self._download_file(self.url, lambda response, _: self.__unzip_project(response, out_dir))

    # TODO: Document
    @staticmethod
    def __unzip_project(response: requests.Response, out_dir: str) -> bool:
        with ZipFile(BytesIO(response.content), 'r') as zip_ref: # type: ZipFile
            zip_ref.extractall(out_dir)
        return True

# URL download file
# TODO: document
class URLProjectFile(ProjectFile):
    
    # TODO: Document
    def __init__(self, url: str, dir: str = os.curdir) -> None:
        super().__init__(dir)
        self.url: str = url
    
    def file_type(self) -> str:
        return 'url'
    
    def to_json(self) -> JsonObject:
        obj: JsonObject = super().to_json()
        obj['url'] = self.url
        return obj

    # TODO: Document
    @staticmethod
    def __write_file(response: requests.Response, file_path: str) -> bool:
        with open(file_path, 'wb') as file: # type: BufferedWriter
            for bytes in response.iter_content(1024): # type: ReadableBuffer
                file.write(bytes)
        return True

    
    def setup(self, out_dir: str) -> bool:
        super().setup(out_dir)
        return self._download_file(self.url, lambda response, filename: self.__write_file(response, self._get_path(out_dir, filename)))

# Git repository project file
# TODO: document
class GitProjectFile(ProjectFile):
    
    __VALID_BRANCH_TYPES: Set[str] = {
        'branch',
        'commit',
        'tag'
    }

    def __init__(self, repository: str, branch: Optional[str] = None, branch_type: str = 'branch', dir: str = os.curdir) -> None:
        super().__init__(dir)
        self.repository: str = repository
        self.branch: Optional[str] = branch
        if branch_type not in self.__VALID_BRANCH_TYPES:
            raise TypeError(f'\"{branch_type}\" is not a valid branch type. Specify {", ".join(__VALID_BRANCH_TYPES)}')
        self.branch_type: str = branch_type
    
    def file_type(self) -> str:
        return "git"
    
    def to_json(self) -> JsonObject:
        obj: JsonObject = super().to_json()
        obj['repository'] = self.repository
        if self.branch is not None:
            obj[self.branch_type] = self.branch
        return obj

    # TODO: Finish
    def setup(self, out_dir: str) -> bool:
        super().setup(out_dir)
        # Checkout and change branches if needed
        repo: Repo = Repo.clone_from(self.repository, self._get_path(out_dir))
        if self.branch is not None:
            repo.git.checkout(self.branch)
        return True

# Project metadata information
# TODO: document
class ProjectMetadata:

    def __init__(self, files: List[ProjectFile]) -> None:
        self.files = files

    # TODO: Implement
    def setup(self, out_dir: str) -> bool:
        failed: List[ProjectFile] = []

        for file in self.files: # type: ProjectFile
            # If the project failed to setup properly, mark it
            if not file.setup(out_dir):
                failed.append(file)
        
        return (not failed)
    
    # TODO: document
    def to_json_object(self) -> JsonObject:
        obj: JsonObject = {}
        obj['files'] = list(map(lambda file: file.to_json(), self.files))
        return obj

    # TODO: document
    def to_json_str(self) -> str:
        return json.dumps(self.to_json_object(), indent = 4)

# TODO: document, implement
def from_json_object(obj: JsonObject) -> ProjectMetadata:
    files: List[ProjectFile] = []
    if 'files' in obj:
        for file in obj['files']: # type: JsonObject
            file_type: str = file['type']
            if file_type == 'osf':
                if 'dir' in file:
                    files.append(OSFProjectFile(file['id'], dir = file['dir']))
                else:
                    files.append(OSFProjectFile(file['id']))
            if file_type == 'url':
                if 'dir' in file:
                    files.append(URLProjectFile(file['url'], dir = file['dir']))
                else:
                    files.append(URLProjectFile(file['url']))
            if file_type == 'git':
                if 'branch' in file:
                    if 'dir' in file:
                        files.append(GitProjectFile(file['repository'], branch = file['branch'], dir = file['dir']))
                    else:
                        files.append(GitProjectFile(file['repository'], branch = file['branch']))
                elif 'tag' in file:
                    if 'dir' in file:
                        files.append(GitProjectFile(file['repository'], branch = file['tag'], branch_type = 'tag', dir = file['dir']))
                    else:
                        files.append(GitProjectFile(file['repository'], branch = file['tag'], branch_type = 'tag'))
                elif 'commit' in file:
                    if 'dir' in file:
                        files.append(GitProjectFile(file['repository'], branch = file['commit'], branch_type = 'commit', dir = file['dir']))
                    else:
                        files.append(GitProjectFile(file['repository'], branch = file['commit'], branch_type = 'commit'))
                else:
                    if 'dir' in file:
                        files.append(GitProjectFile(file['repository'], dir = file['dir']))
                    else:
                        files.append(GitProjectFile(file['repository']))
    return ProjectMetadata(files)

def from_json_str(obj: str) -> ProjectMetadata:
    return from_json_object(json.loads(obj))
