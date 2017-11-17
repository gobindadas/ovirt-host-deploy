#
# ovirt-host-deploy -- ovirt host deployer
# Copyright (C) 2017 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#


"""cockpit configuration plugin."""


import gettext

from otopi import plugin, util


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-host-deploy')


@util.export
class Plugin(plugin.PluginBase):
    """Cockpit configuration plugin.
    """

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
    )
    def _closeup(self):
        self.logger.info(_('Starting Cockpit'))
        if self.services.exists('cockpit'):
            self.services.startup('cockpit', True)
            self.services.state('cockpit', True)
        else:
            self.logger.warning(_('Cockpit not found!'))


# vim: expandtab tabstop=4 shiftwidth=4
