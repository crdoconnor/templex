from commandlib import Command, CommandError
from hitchstory import StoryCollection, BaseEngine, HitchStoryException
from hitchrun import expected
from commandlib import Command
from strictyaml import Str, Map, Int, Optional
from pathquery import pathquery
from commandlib import python
from engine import Engine
from hitchrun import DIR
import hitchpylibrarytoolkit


toolkit = hitchpylibrarytoolkit.ProjectToolkit(
    "templex",
    DIR,
)

@expected(HitchStoryException)
def bdd(*keywords):
    """Run single story."""
    toolkit.bdd(Engine(toolkit.build), keywords)
    

@expected(HitchStoryException)
def regression():
    """Run all stories."""
    clean()
    toolkit.regression(Engine(toolkit.build))
