import sublime
import sublime_plugin
import os
import fnmatch
import re
import mdpopups

from subprocess import Popen, PIPE, call, STDOUT, check_output
# command: goto_file
class GotoFileCommand(sublime_plugin.WindowCommand):
    panelFlags =  sublime.KEEP_OPEN_ON_FOCUS_LOST | sublime.WANT_EVENT
    filefilter = "*" # TODO: make it configurable
    ignoreFolders = [ ".git", ".svn", ".build", ".cache", "zig-cache", "zig-out" ]
    ignoreExts = [ ".bin", ".pdb", ".obj", ".lib", ".o", ".a", ".dll", ".exp", ".exe", ".wasm", ".rdbg", ".blend", ".blend1", ".png", ".fbx", ".g3db", ".g3dj" ]
    items = []
    paths = []

    def cache_folder(self, folder):
        baseFolder = os.path.basename(folder)
        print("cache: ", folder, "->", baseFolder)
        for it in self.ignoreFolders:
            if baseFolder == it:
                print("goto_file: ignore baseFolder:", baseFolder, it)
                return
        for dirpath, dirnames, filenames in os.walk(folder, topdown=True):
            if not filenames:
                continue
            ignore = False
            for it in self.ignoreFolders:
                if it in dirpath:
                    ignore = True
                    break
            if ignore:
                # print("goto_file: ignore:", dirpath)
                continue

            filtered = fnmatch.filter(filenames, self.filefilter)
            if filtered:
                for file in filtered:
                    ignore = False
                    for it in self.ignoreExts:
                        if file.endswith(it):
                            ignore = True
                    if ignore:
                        continue
                    path = "{}{}{}".format(dirpath, os.path.sep, file)
                    localPath = path.replace(folder + os.path.sep, '')

                    # pres = """
                    #     <p style='color=red'> void test(); </p>
                    # """

                    # item = sublime.QuickPanelItem(trigger=localPath, details=[file, path], annotation=baseFolder)

                    item = sublime.QuickPanelItem(trigger=localPath, details=file, annotation=baseFolder)
                    # item = sublime.QuickPanelItem(trigger=file, details=localPath, annotation=baseFolder)
                    # item = sublime.QuickPanelItem(trigger=localPath, details=pres, annotation=baseFolder)
                    self.items.insert(0, item)
                    self.paths.insert(0, path)

    def run(self):
        print("goto_file: running the command")
        self.items = []
        self.paths = []
        folders = self.window.folders()

        def do_show_async():
            for folder in folders:
                self.cache_folder(folder)
            self.window.show_quick_panel(self.items, on_select=self.on_select, flags=self.panelFlags, on_highlight=self.on_highlight, selected_index=-1, placeholder= "Goto File..")

        # sublime.set_timeout_async(do_show_async)
        do_show_async()

    def on_select(self, value, evt):
        print("evt: ", evt)
        if value == -1:
            return
        print("goto_file: selection: {} paths: {} ".format(value, len(self.paths)))
        selected = self.paths[value]
        print("goto_file: open", value, selected)

        flag = 0

        # bring to focus the file if already open
        # if requesting the same file you are viewing, then open it in a new tab
        current = self.window.active_view().file_name()
        if selected == current:
            flag = 256 #sublime.NewFileFlags_FORCE_CLONE

        self.window.open_file(selected, flags=flag)

    def on_highlight(self, value):
        if value == -1:
            return
        # print("goto_file: highlight: {} paths: {} ".format(value, len(self.paths)))
        selected = self.paths[value]
        # print("goto_file: highlight", value, selected)

    def on_done(self, value):
        print("on done")

