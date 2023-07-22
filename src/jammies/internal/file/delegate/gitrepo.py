"""A script obtaining a project file from a git repository.
"""

from typing import Set
from git import Repo
from git.util import rmtree
from jammies.utils import get_default, input_with_default, input_yn_default
from jammies.struct.codec import DictObject
from jammies.defn.file import ProjectFile, ProjectFileCodec
from jammies.defn.builder import build_file
from jammies.registrar import JammiesRegistrar
from jammies.internal.file.gitrepo import _REGISTRY_NAME

def setup_delegate(registrar: JammiesRegistrar) -> None:
    """A setup method used to register components to the project.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    """

     # Create codec
    codec: GitProjectFileCodec = GitProjectFileCodec(registrar)

    registrar.register_file_handler(_REGISTRY_NAME, codec, build_git)

_VALID_BRANCH_TYPES: Set[str] = {
    'branch',
    'commit',
    'tag'
}
"""A set of valid keys indicating the checkout location of the Git repository."""

class GitProjectFile(ProjectFile):
    """A project file for an Git repository."""

    def __init__(self, repository: str, branch_type: str = 'branch',
            branch: str | None = None, **kwargs: DictObject) -> None:
        """
        Parameters
        ----------
        repository : str
            The Git link for the repository location.
        branch_type : str (default 'branch')
            The name of the key holding the branch. Must be within `_VALID_BRANCH_TYPES`.
        branch : str | None (default None)
            The name of the checkout location. If `None`, the default checkout
            location will be used.
        """
        super().__init__(**kwargs)
        self.repository: str = repository
        self.branch: str | None = branch
        if branch_type not in _VALID_BRANCH_TYPES:
            raise ValueError(f"'{branch_type}' is not a valid branch type. "
                + f"Specify one of the following: {', '.join(_VALID_BRANCH_TYPES)}")
        self.branch_type: str = branch_type

    def registry_name(self) -> str:
        return _REGISTRY_NAME

    def setup(self, root_dir: str) -> bool:
        super().setup(root_dir)

        # Checkout and change branches, if applicable
        with Repo.clone_from(self.repository, self._create_path(root_dir)) as repo:
            if self.branch is not None:
                repo.git.checkout(self.branch)

        rmtree(self._create_path(root_dir, '.git'))
        return True

def build_git(registrar: JammiesRegistrar) -> GitProjectFile:
    """Builds a GitProjectFile from user input.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.

    Returns
    -------
    GitProjectFile
        The built project file.
    """
    repository: str = input('Git Repository: ')
    if input_yn_default('Would you like to specify a checkout location', True):
        branch_type: str = input_with_default(
            GitProjectFile, 'branch_type', ', '.join(_VALID_BRANCH_TYPES))
        branch: str | None = input(f'{branch_type.capitalize()} id: ')
    else:
        branch_type: str = get_default(GitProjectFile, 'branch_type')
        branch: str | None = None
    return build_file(registrar, _REGISTRY_NAME, lambda kwargs:
        GitProjectFile(repository, branch = branch, branch_type = branch_type, **kwargs)
    )

class GitProjectFileCodec(ProjectFileCodec[GitProjectFile]):
    """A codec for encoding and decoding a GitProjectFile.
    """

    def encode_type(self, obj: GitProjectFile, dict_obj: DictObject) -> DictObject:
        dict_obj['repository'] = obj.repository
        if obj.branch != get_default(GitProjectFile, 'branch'):
            dict_obj[obj.branch_type] = obj.branch
        return dict_obj

    def decode_type(self, obj: DictObject, **kwargs: DictObject) -> GitProjectFile:
        kwargs['codec'] = self # Set codec
        for branch_name in _VALID_BRANCH_TYPES: # type: str
            if branch_name in obj:
                return GitProjectFile(
                    obj['repository'],
                    branch = obj[branch_name],
                    branch_type = branch_name,
                    **kwargs
                )
        return GitProjectFile(obj['repository'], **kwargs)
