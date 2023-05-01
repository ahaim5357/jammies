"""A script obtaining a project file from a git repository.
"""

import os
from typing import Set, Optional
from git import Repo
from prjman.lazy import SINGLETON
from prjman.utils import get_default
from prjman.struct.codec import DictObject
from prjman.metadata.file import ProjectFile, ProjectFileCodec, build_file

_VALID_BRANCH_TYPES: Set[str] = {
    'branch',
    'commit',
    'tag'
}
"""A set of valid keys indicating the checkout location of the Git repository."""

class GitProjectFile(ProjectFile):
    """A project file for an Git repository."""

    def __init__(self, repository: str, branch: Optional[str] = None,
            branch_type: str = 'branch', rel_dir: str = os.curdir,
            extra: Optional[DictObject] = None) -> None:
        """
        Parameters
        ----------
        repository : str
            The Git link for the repository location.
        branch : str | None (default None)
            The name of the checkout location. If `None`, the default checkout
            location will be used.
        branch_type : str (default 'branch')
            The name of the key holding the branch. Must be within `_VALID_BRANCH_TYPES`.
        rel_dir : str (default '.')
            The directory the project file is located.
        extra : dict[str, Any]
            Extra data defined by the user.
        """
        super().__init__(rel_dir, extra)
        self.repository: str = repository
        self.branch: Optional[str] = branch
        if branch_type not in _VALID_BRANCH_TYPES:
            raise ValueError(f'\"{branch_type}\" is not a valid branch type. \
                Specify one of the following: {", ".join(_VALID_BRANCH_TYPES)}')
        self.branch_type: str = branch_type

    def codec(self) -> 'ProjectFileCodec':
        return SINGLETON.GIT_FILE_CODEC

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)

        # Checkout and change branches, if applicable
        repo: Repo = Repo.clone_from(self.repository, self._create_path(root_dir))
        if self.branch is not None:
            repo.git.checkout(self.branch)
        return True

def build_git() -> GitProjectFile:
    """Builds a GitProjectFile from user input.
    
    Returns
    -------
    GitProjectFile
        The built project file.
    """
    repository: str = input('Git Repository: ')
    def_branch_type: str = get_default(GitProjectFile, 'branch')
    branch_type: str = \
        input(f"{', '.join(_VALID_BRANCH_TYPES)} (default '{def_branch_type}'): ").lower()
    branch: Optional[str] = input(f"{branch_type} (default branch): ")
    if not branch:
        branch = None
    return build_file(lambda rel_dir:
        GitProjectFile(repository, branch = branch, branch_type = branch_type, rel_dir = rel_dir)
    )

class GitProjectFileCodec(ProjectFileCodec[GitProjectFile]):
    """A codec for encoding and decoding a GitProjectFile.
    """

    def encode_type(self, obj: GitProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['repository'] = obj.repository
        if obj.branch != get_default(GitProjectFile, 'branch'):
            dict_obj[obj.branch_type] = obj.branch
        return dict_obj

    def decode_type(self, rel_dir: str, extra: Optional[DictObject],
            obj: DictObject) -> GitProjectFile:
        for branch_name in _VALID_BRANCH_TYPES: # type: str
            if branch_name in obj:
                return GitProjectFile(
                    obj['repository'],
                    branch = obj[branch_name],
                    branch_type = branch_name, rel_dir = rel_dir
                )
        return GitProjectFile(obj['repository'], rel_dir = rel_dir, extra = extra)
