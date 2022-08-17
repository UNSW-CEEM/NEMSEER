# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Types of Contributions

### Report Bugs

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

You can never have enough documentation! Please feel free to contribute to any
part of the documentation, such as the official docs, docstrings, or even
on the web in blog posts, articles, and such.

### Submit Feedback

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `nemseer` for local development.

1. Download a copy of `nemseer` locally.
2. Install `poetry`

    - `poetry` is changing the way dependencies are managed, so as of July 2022, install `v1.2.0b2` (we will transition to `v1.2.0` once it is released)
    - The command below applies to UNIX systems (Mac/Linux)

        ```console
        $ curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0b2
        ```

    - The command below applies to Windows. Run it in PowerShell (make sure you run PowerShell as an administrator).
      - You will also need to add the Poetry bin directory (printed during install) [to your PATH environment variable](https://stackoverflow.com/questions/44272416/how-to-add-a-folder-to-path-environment-variable-in-windows-10-with-screensho)
      - For activating environments etc. you may need to alter your [PowerShell Execution Policy to `RemoteSigned`](https://windowsloop.com/change-powershell-execution-policy/)

        ```powershell
          (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py - --version=1.2.0b2
        ```

3. Install `nemseer` using `poetry`:

    - Developers should install additional `poetry` groups for development:
      - `docs` for documentation dependencies
      - `lint` for linters. `nemseer` uses `flake8` and `mypy` for type annotations
      - `test` for testing utilities
      - (optional) `debug` for debugging tools

        ```console
        $ poetry install --with=docs,lint,test
        ```

    - If you are on Windows and attempting to install dependencies results in an error such as the one below, refer to the [fix below](https://github.com/UNSW-CEEM/NEMSEER/blob/master/CONTRIBUTING.md#fix-for-running-poetry-on-windows):

      ```cmd
      Command "C:\Users\Abi Prakash\AppData\Local\Programs\Python\Python38\python.exe" -W ignore - errored with the following return code 1, and output:
      The system cannot find the path specified.
      C:\Users\Abi Prakash\AppData\Local\Programs\Python\Python38
      input was : import sys

      if hasattr(sys, "real_prefix"):
          print(sys.real_prefix)
      elif hasattr(sys, "base_prefix"):
          print(sys.base_prefix)
      else:
          print(sys.prefix)
      ```
    - Use the virtual env in your terminal by running `poetry shell`, or direct your favourite text editor to the poetry environment

4. Use `git` (or similar) to create a branch for local development and make your changes:

    ```console
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

5. When you're done making changes, check that your changes conform to any code formatting requirements and pass any tests.

6. Commit your changes and open a pull request.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the docs should be updated.
3. The pull request should work for all currently supported operating systems and versions of Python.

## Fix for running `poetry` on Windows

If you get an error message similar to the one above, or one that returns an `EnvCommandError` when you run `poetry install -vv` follow these steps.

We will implement the fix described [here](https://github.com/python-poetry/poetry/issues/2746#issuecomment-739439858):

1. Find where `poetry` source files are located. We are interested in `env.py`.

    - They are likely to be here: `C:\Users\<USER>\AppData\Roaming\pypoetry\venv\Lib\site-packages\poetry\utils`
    - If they are not, run `poetry install -vv` to get a stack trace and find where `env.py` is located (this should be in the stack trace)
2. Find the `_run` method of class `Env`
3. Comment out and add lines as demonstrated below (this is done in the last three line of the code block below)

    ```python
    def _run(self, cmd: list[str], **kwargs: Any) -> int | str:
    """
    Run a command inside the Python environment.
    """
    call = kwargs.pop("call", False)
    input_ = kwargs.pop("input_", None)
    env = kwargs.pop("env", dict(os.environ))

    try:
        #if self._is_windows:
        #    kwargs["shell"] = True
        kwargs["shell"] = False
    ```

## Code of Conduct

Please note that the `nemseer` project is released with a
[Code of Conduct](docs/source/conduct.md). By contributing to this project you agree to abide by its terms.
