from hitchstory import InfoDefinition, InfoProperty
from strictyaml import Seq, Enum
import hitchpylibrarytoolkit


class Engine(hitchpylibrarytoolkit.Engine):
    info_definition = InfoDefinition()

    def assert_text(self, will_output, actual_output):
        assert will_output == actual_output, \
            "GOT:\n{}\n\nEXPECTED:\n{}\n".format(will_output, actual_output)

    def set_up(self):
        self._build.ensure_built()

        for filename, contents in self.given.get('files', {}).items():
            filepath = self._build.working.parent.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(contents)
