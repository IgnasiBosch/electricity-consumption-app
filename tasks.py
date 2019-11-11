import os
import pathlib
import re
import webbrowser

from invoke import task
from invoke.exceptions import Exit, ParseError


PACKAGE = "app"
TEST_PACKAGE = "tests"
TYPECHECK_PATH = ".typing_modules"
TYPECHECK_KNOWN_MISSING_MODULES = ["aiohttp", "asynctest", "invoke", "pytest"]
MIN_COVERAGE = os.environ.get("MIN_TEST_COVERAGE", 70)


LINT_BITS = {}
LINT_MASKS = {}
LINT_USAGE_ERROR = 32
for n, field in enumerate(["fatal", "error", "warning", "refactor", "convention"]):
    LINT_BITS[field] = 1 << n
    LINT_MASKS[field] = (2 << n) - 1 + LINT_USAGE_ERROR


_PATTERNS = [
    r"^{}/".format(TYPECHECK_PATH),  # outside our purview
    r"error: Unexpected keyword argument",  # attrs magic
    r"error: No library stub file for module 'pytest'",
    r"note: \(Stub files are from",  # noise
    r"note: \(Perhaps setting MYPYPATH or using",  # noise
]
_PATTERNS += [
    f"Cannot find module named '{module}" for module in TYPECHECK_KNOWN_MISSING_MODULES
]

TYPECHECK_IGNORES = [re.compile(p) for p in _PATTERNS]


def _header(text, border_char="-"):
    border = border_char * len(text)
    print(f"{border}\n{text}\n{border}")


@task(
    help={
        "threshold": "Message level to fail on or over. Can be one of {}".format(
            ", ".join(repr(m) for m in LINT_MASKS)
        )
    }
)
def lint(ctx, threshold="error"):
    """
    Run PyLint to check the package and test code.

    By default runs at an "error" threshold, but can be more stringent. The
    checks on the test code are fixed at the "error" threshold. PyLint is not
    perfect, occasionally you'll need to add a # pylint: disable=some-flag to
    lines that misbehave (see __main__.py)
    """
    try:
        exit_mask = LINT_MASKS[threshold]
    except KeyError:
        raise ParseError(
            "Unkown threshold flag {!r}. Must be one of {}".format(
                threshold, list(LINT_MASKS)
            )
        )

    result = ctx.run(f"pylint --rcfile=setup.cfg {PACKAGE}", warn=True, pty=True)
    if result.return_code & exit_mask:
        raise Exit(f"PyLint returned with {threshold} bits or higher set")

    ctx.run(f"pylint -E --rcfile=setup.cfg {TEST_PACKAGE}")


def extract_metadata(path: pathlib.Path) -> str:
    """Look in a folder for the metadata file and return the pinned package
    version it has, e.g. 'aiohttp==3.1.2'. Returns ``None`` on failure."""
    if path.name.endswith(".egg-info"):
        metadata_file = "PKG-INFO"
    elif path.name.endswith(".dist-info"):
        metadata_file = "METADATA"
    else:
        return  # this isn't a package directory

    key_search = {"Name", "Version"}
    data = {}
    try:
        with open(path / metadata_file, "r") as f:
            for line in f:
                try:
                    key, value = (part.strip() for part in line.split(":", 1))
                    key_search.remove(key)
                except ValueError:
                    continue  # some other line without a colon
                except KeyError:
                    continue  # already found the key/not one we care about
                data[key] = value
                if not key_search:
                    return "{Name}=={Version}".format(**data)
    except OSError:
        return  # failed to open file (or read it or whatever)


@task(help={"force_reinstall": "Delete/recreate the contents of MYPYPATH"})
def typecheck(ctx, force_reinstall=False):
    """Run mypy, including against selected 3rd party packages without stubs

    Installs selected packages with annotations into a local scratch directory
    and instructs mypy to refer to them via MYPYPATH. Workaround for packages
    that don't provide stubs and/or aren't in typeshed. If too much is
    installed into it, or MYPYPATH was to be set to PYTHONPATH, there would
    be an overwhelming amount of false-positives.

    Package versions are determined by looking at Pipfile.lock
    """

    typecheck = pathlib.Path(TYPECHECK_PATH)
    typecheck.mkdir(exist_ok=True)

    mypy_flags = [
        "--ignore-missing-imports",
        f"--package {PACKAGE}",
        f"--package {TEST_PACKAGE}",
    ]
    result = ctx.run(
        "mypy {}".format(" ".join(mypy_flags)),
        warn=True,
        hide="stdout",
        env={"MYPYPATH": TYPECHECK_PATH},
    )

    lines = [
        line
        for line in result.stdout.splitlines()
        if not any(re.search(pattern, line) for pattern in TYPECHECK_IGNORES)
    ]

    for line in lines:
        print(line)


@task
def format(ctx):
    """Format the codes"""
    ctx.run("black .")


@task
def style(ctx):
    """Style checking

    Some ignores are configured in setup.cfg. Try not to overlap too much with
    pylint. What rules should be ignored/configured off default is worthy
    of debate.
    """
    ctx.run("black --check .")
    ctx.run(f"flake8 {PACKAGE}")


@task
def test(ctx):
    """Run pytest with coverage, generating the report"""
    ctx.run(
        f"coverage run --source {PACKAGE} -m pytest {TEST_PACKAGE} --color=yes", env={}
    )
    ctx.run(f"coverage report --fail-under={MIN_COVERAGE}")
    ctx.run("coverage html")
    ctx.run("coverage xml")


@task
def showcov(ctx):
    """Open report in a web browser"""
    target = "htmlcov/index.html"
    if not pathlib.Path(target).exists():
        raise Exit("Can't find HTML report")
    webbrowser.open(target)


@task
def suite(ctx):
    _header("Linting")
    lint(ctx)
    _header("Typechecking")
    typecheck(ctx)
    _header("Style")
    style(ctx)
    _header("Testing")
    test(ctx)
