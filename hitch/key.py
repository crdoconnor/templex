from commandlib import run
import hitchpython
from hitchstory import StoryCollection, StorySchema, BaseEngine, exceptions
from hitchrun import expected
from commandlib import Command
from strictyaml import Str, Map, Int, Optional, load
from pathquery import pathq
import hitchtest
import hitchdoc
from hitchrun import hitch_maintenance
from commandlib import python
from hitchrun import DIR
from hitchrun.decorators import ignore_ctrlc


from jinja2.environment import Environment
from jinja2 import DictLoader


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
        from hitchrunpy import ExamplePythonCode

        ExamplePythonCode(
            self.preconditions['code']
        ).with_setup_code(self.preconditions.get('setup', ''))\
         .run(self.path.state, self.python)

    def raises_exception(self, exception_type=None, message=None):
        """
        Expect an exception.
        """
        from hitchrunpy import ExamplePythonCode

        ExamplePythonCode(
            self.preconditions['code']
        ).with_setup_code(self.preconditions.get('setup', ''))\
         .expect_exception(exception_type, message.rstrip())\
         .run(self.path.state, self.python)

        """
        class ExpectedExceptionDidNotHappen(Exception):
            pass

        error_path = self.path.state.joinpath("error.txt")
        runpy = self.path.gen.joinpath("runmypy.py")
        if error_path.exists():
            error_path.remove()
        env = Environment()
        env.loader = DictLoader(
            load(self.path.key.joinpath("codetemplates.yml").bytes().decode('utf8')).data
        )
        runpy.write_text(env.get_template("raises_exception").render(
            setup=self.preconditions['setup'],
            code=self.preconditions['code'],
            variables=self.preconditions.get('variables', None),
            yaml_snippet=self.preconditions.get("yaml_snippet"),
            modified_yaml_snippet=self.preconditions.get("modified_yaml_snippet"),
            exception=exception,
            error_path=error_path,
        ))
        self.python(runpy).run()
        if not error_path.exists():
            raise ExpectedExceptionDidNotHappen()
        else:
            import difflib
            actual_error = error_path.bytes().decode('utf8')
            if not exception.strip() in actual_error:
                raise Exception(
                    "actual:\n{0}\nexpected:\n{1}\ndiff:\n{2}".format(
                        actual_error,
                        exception,
                        ''.join(difflib.context_diff(exception, actual_error)),
                    )
                )
        """

    def should_be_equal_to(self, rhs):
        """
        Code should be equal to rhs
        """
        class UnexpectedException(Exception):
            pass

        error_path = self.path.gen.joinpath("error.txt")
        runpy = self.path.gen.joinpath("runmypy.py")
        if error_path.exists():
            error_path.remove()
        env = Environment()
        env.loader = DictLoader(
            load(self.path.key.joinpath("codetemplates.yml").bytes().decode('utf8')).data
        )
        runpy.write_text(env.get_template("shouldbeequal").render(
            setup=self.preconditions['setup'],
            code=self.preconditions['code'],
            variables=self.preconditions.get('variables', None),
            yaml_snippet=self.preconditions.get("yaml_snippet"),
            modified_yaml_snippet=self.preconditions.get("modified_yaml_snippet"),
            rhs=rhs,
            error_path=error_path,
        ))
        self.python(runpy).run()
        if error_path.exists():
            raise UnexpectedException(error_path.bytes().decode("utf8"))

    def on_failure(self, result):
        if self.settings.get("pause_on_failure", True):
            if self.preconditions.get("launch_shell", False):
                self.services.log(message=self.stacktrace.to_template())

    def pause(self, message="Pause"):
        if hasattr(self, 'services'):
            self.services.start_interactive_mode()
        import IPython
        IPython.embed()
        if hasattr(self, 'services'):
            self.services.stop_interactive_mode()

    def on_success(self):
        if self.settings.get("overwrite"):
            self.new_story.save()

    def tear_down(self):
        try:
            self.shutdown_connection()
        except:
            pass
        if hasattr(self, 'services'):
            self.services.shutdown()


def _storybook(settings):
    return StoryCollection(pathq(DIR.key).ext("story"), Engine(DIR, settings))


@expected(exceptions.HitchStoryException)
def tdd(*words):
    """
    Run all tests
    """
    print(
        _storybook({}).shortcut(*words).play().report()
    )


@expected(exceptions.HitchStoryException)
def testfile(filename):
    """
    Run all stories in filename 'filename'.
    """
    print(
        _storybook({}).in_filename(filename).ordered_by_name().play().report()
    )


@expected(exceptions.HitchStoryException)
def regression():
    """
    Run regression testing - lint and then run all tests.
    """
    lint()
    print(
        _storybook({}).ordered_by_name().play().report()
    )


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


@ignore_ctrlc
def ipy():
    """
    Run IPython in environment."
    """
    Command(DIR.gen.joinpath("py3.5.0", "bin", "ipython")).run()
