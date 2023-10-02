import sublime
import sublime_plugin
import os
import fnmatch
import re

# command: goto_file
class GotoFileCommand(sublime_plugin.WindowCommand):
    panelFlags = sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST
    filefilter = "*" # TODO: make it configurable
    ignoreFolders = [ ".git", ".svn", ".build", ".cache" ]
    ignoreExts = [ ".pdb", ".obj", ".lib", ".exp", ".exe", ".wasm", ".rdbg" ]
    items = []
    paths = []

    def cache_folder(self, folder):
        baseFolder = os.path.basename(folder)
        print("cache: ", folder, "->", baseFolder)
        for it in self.ignoreFolders:
            if baseFolder in it:
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
                    item = sublime.QuickPanelItem(trigger=localPath, details=[file, path], annotation=baseFolder)
                    self.items.insert(0, item)
                    self.paths.insert(0, path)

    def run(self):
        print("goto_file: running the command")
        self.items = []
        self.paths = []
        folders = self.window.folders()

        if len(folders) > 1:
            self.usePrefix = True

        for folder in folders:
            self.cache_folder(folder)

        self.window.show_quick_panel(self.items, self.check_selection, self.panelFlags, placeholder= "Enter a Path name")
        print("goto_file: items len: {}".format(len(self.items)))

    def check_selection(self, value):
        if value == -1:
            return
        print("goto_file: selection: {} paths: {} ".format(value, len(self.paths)))
        selected = self.paths[value]
        print("goto_file: open", value, selected)
        self.window.open_file(selected)
