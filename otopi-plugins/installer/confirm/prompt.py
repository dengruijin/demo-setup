from otopi import constants
from otopi import plugin
from otopi import util



@util.export
class Plugin(plugin.PluginBase):
    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(stage=plugin.Stages.STAGE_INIT)
    def _init(self):
        self.environment.setdefault('enabled', None)


    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        name="CONFIRM_INSTALL",
    )
    def _customization(self):
        if self.environment['enabled'] is None:
            self.environment['enabled'] = (
                self.dialog.queryString(
                    name='CONFIRM_INSTALL_DIALOG',
                    note=('Setup demo program on this host (@VALUES@) [@DEFAULT@]: '),
                    prompt=True,
                    validValues=('Yes','No'),
                    caseSensitive=False,
                    default='Yes',
                ) != 'no'
            )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name="MISC_INSTALL",
    )
    def _misc(self):
        self.dialog.note( text='enabled=%s' % self.environment['enabled'])
        self.logger.warn( 'enabled=%s' % self.environment['enabled'])
