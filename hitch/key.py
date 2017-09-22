from commandlib import run, CommandError
import hitchpython
from hitchstory import StoryCollection, StorySchema, BaseEngine, HitchStoryException
from hitchrun import expected
from commandlib import Command
from strictyaml import Str, Map, Int, Optional
from pathquery import pathq
import hitchtest
import hitchdoc
from hitchrun import hitch_maintenance
from commandlib import python
from hitchrun import DIR
from hitchrun.decorators import ignore_ctrlc
from hitchrunpy import ExamplePythonCode


class Engine(BaseEngine):
    """Python engine for running tests."""
    schema = StorySchema(
        preconditions=Map({
            "python version": Str(),
            "setup": Str(),
            "code": Str(),
        }),
        params=Map({
            "python version": Str(),
        }),
        about={
            "description": Str(),
            Optional("importance"): Int(),
        },
    )

    def __init__(self, keypath, settings):
        self.path = keypath
        self.settings = settings

    def set_up(self):
        """Set up your applications and the test environment."""
        self.doc = hitchdoc.Recorder(
            hitchdoc.HitchStory(self),
            self.path.gen.joinpath('storydb.sqlite'),
        )

        if self.path.gen.joinpath("state").exists():
            self.path.gen.joinpath("state").rmtree(ignore_errors=True)
        self.path.gen.joinpath("state").mkdir()
        self.path.state = self.path.gen.joinpath("state")

        for filename, text in self.preconditions.get("files", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().mkdir()
            filepath.write_text(text)

        self.python_package = hitchpython.PythonPackage(
            self.preconditions['python version']
        )
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        # Install debugging packages
        with hitchtest.monitor([self.path.key.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                run(self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.key))

        # Uninstall and reinstall
        with hitchtest.monitor(
            pathq(self.path.project.joinpath("templex")).ext("py")
        ) as changed:
            if changed:
                run(self.pip("uninstall", "templex", "-y").ignore_errors())
                run(self.pip("install", ".").in_dir(self.path.project))

    def run_code(self):
        ExamplePythonCode(
            self.preconditions['code']
        ).with_setup_code(self.preconditions.get('setup', ''))\
         .run(self.path.state, self.python)

    def raises_exception(self, exception_type=None, message=None):
        """
        Expect an exception.
        """
        result = ExamplePythonCode(
            self.preconditions['code']
        ).with_setup_code(self.preconditions.get('setup', ''))\
         .expect_exceptions()\
         .run(self.path.state, self.python)

        result.exception_was_raised(exception_type, message)

    def should_be_equal_to(self, rhs):
        ExamplePythonCode(
            self.preconditions.get('setup', '')
        ).is_equal(self.preconditions['code'], rhs)\
         .run(self.path.state, self.python)

    def pause(self, message="Pause"):
        import IPython
        IPython.embed()

    def on_success(self):
        if self.settings.get("overwrite"):
            self.new_story.save()


def _storybook(settings):
    return StoryCollection(pathq(DIR.key).ext("story"), Engine(DIR, settings))


@expected(HitchStoryException)
def tdd(*words):
    """
    Run all tests
    """
    print(
        _storybook({}).shortcut(*words).play().report()
    )


@expected(HitchStoryException)
def testfile(filename):
    """
    Run all stories in filename 'filename'.
    """
    print(
        _storybook({}).in_filename(filename).ordered_by_name().play().report()
    )


@expected(HitchStoryException)
def regression():
    """
    Run regression testing - lint and then run all tests.
    """
    print(
        _storybook({}).ordered_by_name().play().report()
    )
    lint()


@expected(CommandError)
def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("templex"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "templex"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


def docgen():
    """
    Generate documentation.
    """
    docpath = DIR.project.joinpath("docs")

    if not docpath.exists():
        docpath.mkdir()

    documentation = hitchdoc.Documentation(
        DIR.gen.joinpath('storydb.sqlite'),
        'doctemplates.yml'
    )

    for story in documentation.stories:
        story.write(
            "rst",
            docpath.joinpath("{0}.rst".format(story.slug))
        )


@expected(CommandError)
@ignore_ctrlc
def rerun(version="2.7.10"):
    """
    Rerun last example code block with specified version of python.
    """
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        DIR.gen.joinpath("state", "examplepythoncode.py")
    ).in_dir(DIR.gen.joinpath("state")).run()
