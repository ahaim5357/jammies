"""TODO: Document, implement, finish"""

from typing import TypeAlias, Callable, TypeVar, List, Tuple
from jammies.registrar import JammiesRegistrar
from jammies.defn.file import ProjectFile, PostProcessor
from jammies.struct.codec import DictObject
from jammies.utils import input_with_default, input_yn_default

ProjectFileBuilder: TypeAlias = Callable[[JammiesRegistrar], ProjectFile]
"""A supplier used to construct a ProjectFile from an user's input."""

PF = TypeVar('PF', bound = ProjectFile)
"""The type of the project file."""

def build_file(registrar: JammiesRegistrar, codec_name: str, callback: Callable[[DictObject], PF]) -> PF:
    """Builds a ProjectFile from user input based on the
    passed in callback.
    
    Parameters
    ----------
    registrar : `JammiesRegistrar`
        The registrar used to register the components for the project.
    codec_name : str
        The name of the codec for the project file.
    callback : (kwargs) -> ProjectFile
        A function that takes in the arguments of the ProjectFile
        and returns the completed ProjectFile.
    
    Returns
    -------
    ProjectFile
        The built project file.
    """
    kwargs: DictObject = {
        'codec': registrar.get_project_file_codec(codec_name),
        'name': input_with_default(ProjectFile, 'name', 'Name of the project file'),
        'rel_dir': input_with_default(ProjectFile, 'rel_dir', 'Directory to extract to'),
    }

    # Post processors
    post_processor: str = input_with_default(ProjectFile, 'post_processor',
        'Post processor on file')
    kwargs['post_processor'] = post_processor if post_processor is None \
        else (registrar.get_post_processor(post_processor), { 'type': post_processor})

    return callback(kwargs)
