# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/gpl-3.0.txt

from ..base import torrent as base
from . import _mixin as mixin
from .. import ExpectedResource
from ._common import make_tab_title_widget
from ...completion import candidates

from functools import partial


class AddTorrentsCmd(base.AddTorrentsCmdbase,
                     mixin.polling_frenzy, mixin.make_request):
    provides = {'tui'}


class TorrentDetailsCmd(base.TorrentDetailsCmdbase,
                        mixin.select_torrents, mixin.make_request):
    provides = {'tui'}
    tui = ExpectedResource

    async def display_details(self, torrent_id):
        make_titlew = partial(make_tab_title_widget,
                              attr_unfocused='tabs.torrentdetails.unfocused',
                              attr_focused='tabs.torrentdetails.focused')

        from ...tui.views.details import TorrentDetailsWidget
        TorrentDetailsWidget_keymapped = self.tui.keymap.wrap(TorrentDetailsWidget,
                                                              context='torrent')
        title_str = self.title if hasattr(self, 'title') else None
        detailsw = TorrentDetailsWidget_keymapped(self.srvapi, torrent_id, title=title_str)
        tabid = self.tui.tabs.load(make_titlew(detailsw.title), detailsw)

        def set_tab_title(text):
            # set_title() throws IndexError if the tab was removed, which may
            # have happened while TorrentDetailsWidget was waiting for a
            # response.
            try:
                self.tui.tabs.set_title(make_titlew(text), position=tabid)
            except IndexError:
                pass
        detailsw.title_updater = set_tab_title


class ListTorrentsCmd(base.ListTorrentsCmdbase,
                      mixin.select_torrents,
                      mixin.create_list_widget):
    provides = {'tui'}

    def make_torrent_list(self, tfilter, sort, columns):
        from ...tui.views.torrent_list import TorrentListWidget
        self.create_list_widget(TorrentListWidget, theme_name='torrentlist',
                                tfilter=tfilter, sort=sort, columns=columns,
                                markable_items=True)


class TorrentMagnetURICmd(base.TorrentMagnetURICmdbase,
                          mixin.select_torrents):
    provides = {'tui'}

    def display_uris(self, uris):
        for uri in uris:
            self.info(uri)


class MoveTorrentsCmd(base.MoveTorrentsCmdbase,
                      mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}

    @classmethod
    async def completion_candidates_posargs(cls, args):
        """Complete positional arguments"""
        def dest_path_candidates(curarg):
            return candidates.fs_path(curarg.before_cursor,
                                      base=cls.srvcfg['path.complete'],
                                      directories_only=True)

        curarg = args.curarg
        if len(args) >= 3:
            if args.curarg_index == 1:
                return await candidates.torrent_filter(curarg)
            elif args.curarg_index == 2:
                return dest_path_candidates(curarg)
        elif len(args) == 2:
            # Single argument may be a path or a filter
            filter_cands = await candidates.torrent_filter(curarg)
            path_cands = dest_path_candidates(curarg)
            return (path_cands,) + filter_cands


class RemoveTorrentsCmd(base.RemoveTorrentsCmdbase,
                        mixin.polling_frenzy, mixin.make_request, mixin.select_torrents,
                        mixin.ask_yes_no):
    provides = {'tui'}
    cmdmgr = ExpectedResource
    CONFIRMATION_TAB_TITLE = 'Removal Confirmation'

    async def show_list_of_hits(self, tfilter):
        cmd = 'tab --title %r ls --sort name %s' % (self.CONFIRMATION_TAB_TITLE, tfilter)
        await self.cmdmgr.run_async(cmd)

    async def remove_list_of_hits(self):
        cmd = 'tab --close %r --focus left' % self.CONFIRMATION_TAB_TITLE
        await self.cmdmgr.run_async(cmd)


class RenameTorrentCmd(base.RenameTorrentCmdbase,
                       mixin.polling_frenzy, mixin.make_request, mixin.select_torrents, mixin.select_files):
    provides = {'tui'}


class StartTorrentsCmd(base.StartTorrentsCmdbase,
                       mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}


class StopTorrentsCmd(base.StopTorrentsCmdbase,
                      mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}


class VerifyTorrentsCmd(base.VerifyTorrentsCmdbase,
                        mixin.make_request, mixin.select_torrents):
    provides = {'tui'}
