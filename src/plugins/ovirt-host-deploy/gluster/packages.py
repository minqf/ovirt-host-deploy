#
# ovirt-host-deploy -- ovirt host deployer
# Copyright (C) 2012-2013 Red Hat, Inc.
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


"""gluster psackages plugin."""


import gettext


from otopi import plugin
from otopi import util


from ovirt_host_deploy import constants as odeploycons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-host-deploy')


@util.export
class Plugin(plugin.PluginBase):
    """Gluster pacakges.

    Environment:
        GlusterEnv.ENABLE -- perform gluster customization.

    """
    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = False

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment[odeploycons.GlusterEnv.ENABLE] = False

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
        condition=lambda self: (
            self.environment[odeploycons.GlusterEnv.ENABLE]
        ),
    )
    def _validation(self):
        if not self.packager.queryPackages(patterns=('vdsm-gluster',)):
            raise RuntimeError(
                _(
                    'Cannot locate gluster packages, '
                    'possible cause is incorrect channels'
                )
            )
        self._enabled = True

    @plugin.event(
        stage=plugin.Stages.STAGE_PACKAGES,
        condition=lambda self: self._enabled,
    )
    def _packages(self):
        self.packager.installUpdate(('vdsm-gluster',))

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: (
            self._enabled and
            not self.environment[
                odeploycons.CoreEnv.FORCE_REBOOT
            ]
        ),
    )
    def _closeup(self):
        self.logger.info(_('Starting gluster'))
        self.services.startup('glusterd', True)
        self.services.state('glusterd', True)
        if self.services.exists('glustereventsd'):
            self.logger.info(_('Starting glustereventsd'))
            self.services.startup('glustereventsd', True)
            self.services.state('glustereventsd', True)

# vim: expandtab tabstop=4 shiftwidth=4
