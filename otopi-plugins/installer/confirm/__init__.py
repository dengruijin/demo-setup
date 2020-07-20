from otopi import util
from . import prompt

@util.export
def createPlugins(context):
    prompt.Plugin(context=context)

