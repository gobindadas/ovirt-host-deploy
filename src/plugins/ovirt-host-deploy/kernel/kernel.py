#
# ovirt-host-deploy -- ovirt host deployer
# Copyright (C) 2016 Red Hat, Inc.
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


"""vdsm kernel command line management plugin."""


import gettext

from otopi import constants as otopicons
from otopi import plugin
from otopi import transaction
from otopi import util

from ovirt_host_deploy import constants as odeploycons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-host-deploy')


@util.export
class Plugin(plugin.PluginBase):
    """Grubby plugin.

    Environment:
        KernelEnv.CMDLINE_NEW -- string containing new custom kernel command
                                 line part
        KernelEnv.CMDLINE_OLD -- string containing old parameters for kernel
                                 command line
    """

    _GRUBBY_PKG = 'grubby'

    class KernelSetupTransaction(transaction.TransactionElement):

        def __init__(self, parent):
            self._parent = parent

        def __str__(self):
            return _("KernelSetup Transaction")

        def prepare(self):
            pass

        def abort(self):
            self._parent.logger.debug('Rollback kernel transaction')
            self._parent.execute(
                self._parent._build_grubby_command(
                    revert=True,
                ),
            )

            self._parent.execute(
                self._parent._build_grubby_command(
                    revert=True,
                    remove_args=False,
                ),
            )

        def commit(self):
            self._parent.logger.info('Setting kernel arguments')
            self._parent.execute(
                self._parent._build_grubby_command(),
            )
            self._parent.execute(
                self._parent._build_grubby_command(
                    remove_args=False,
                ),
            )

    @plugin.event(stage=plugin.Stages.STAGE_INIT)
    def _init(self):
        self._enabled = False

        self.environment.setdefault(odeploycons.KernelEnv.CMDLINE_NEW, None)
        self.environment.setdefault(odeploycons.KernelEnv.CMDLINE_OLD, None)

        self.command.detect('grubby')

    @plugin.event(stage=plugin.Stages.STAGE_VALIDATION)
    def _validation(self):
        if self.command.get('grubby', optional=True):
            self._enabled = True
        else:
            self.logger.warn(
                'Grubby not present - not setting kernel arguments.'
            )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: self._enabled,
    )
    def _misc(self):
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            self.KernelSetupTransaction(
                parent=self,
            )
        )

    def _build_grubby_command(self, remove_args=True, revert=False):
        cmd = [self.command.get('grubby'), '--update-kernel', 'DEFAULT']

        new, old = (
            odeploycons.KernelEnv.CMDLINE_NEW,
            odeploycons.KernelEnv.CMDLINE_OLD,
        )
        if revert:
            new, old = old, new

        if remove_args:
            if self.environment[old]:
                cmd += ['--remove-args',
                        self.environment[old]]
        else:
            if self.environment[new]:
                cmd += ['--args',
                        self.environment[new]]

        return cmd