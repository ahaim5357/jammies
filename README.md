# jammies

`jammies` is a helper for constructing, managing, and patching projects to better improve and fix the reproducibility of other work.

## Project Files

'Project Files' indicate a method of grabbing a file(s) from some location to put into the working directory. Each project file can specify a relative directory to the working directory of where to extract to.

The following project file types are supported:

* osf - An Open Science Framework project
* git - A git repository
* url - An arbitrary url to obtain a file via a GET request

## Project Metadata Specification

The `project_metadata.json` generated with each project looks like so:

```js
{
    "files": [
        {
            "type": "xxx", // Must be "osf", "url", or "git"
            "dir": "<path>", // The directory relative to the working directory to put the file in (default: the working directory)
            "extra": {
                // An object containing user-defined data
            }
        }
        {
            "type": "osf",
            "id": "<project_id>" // The five alphanumeric character OSF project identifier 
        },
        {
            "type": "url",
            "url": "<url>" // A url to query a file from via a GET request
        },
        {
            "type": "git",
            "repository": "<git_repo>", // The git repository to checkout
            "branch|tag|commit": "<branch_name>|<tag_name>|<commit_id>" // The location to checkout to (default: the default branch when cloning the repository)
        }
    ],
    "ignore": [
        // A list of file patterns to ignore instead of patching if it exists.
        "xxx"
    ],
    "overwrite": [
        // A list of file patterns to overwrite instead of patching if it exists.
        "xxx"
    ],
    "extra": {
        // An object containing user-defined data
    }
}
```

## Commands

The following commands can be accessed from the command line interface:

* `jammies patch init [--import_metadata/-I <path_or_url>]`
    * Initializes a new project to be patched either from the metadata in the current directory, an import, or provided via the builder.
    * Optional Parameters:
        * `--import_metadata/-I` - Takes in a path or url to the metadata JSON to build the project for.
* `jammies patch clean [--import_metadata/-I <path_or_url>]`
    * Initializes a clean workspace either from the metadata in the current directory, an import, or provided via the builder.
    * Optional Parameters:
        * `--import_metadata/-I` - Takes in a path or url to the metadata JSON to build the project for.
* `jammies patch src [--import_metadata/-I <path_or_url>]`
    * Initializes a patched workspace either from the metadata in the current directory, an import, or provided via the builder.
    * Optional Parameters:
        * `--import_metadata/-I` - Takes in a path or url to the metadata JSON to build the project for.
* `jammies patch output`
    * Generates any patches from the original files and clones the new files to an output directory.

## Contributing

`prjmn` is built for Python 3.8+ while being developed on 3.11.
