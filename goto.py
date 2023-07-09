import sublime
import sublime_plugin
import os
import fnmatch

# command: goto_file
class GotoFileCommand(sublime_plugin.WindowCommand):
    panelFlags = sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST
    filefilter = "*" # TODO: make it configurable
    ignoreFolders = [ ".git", ".svn", ".build", ".cache" ]
    items = []
    paths = []
    times = {}
    cachedItems = {}
    cachedPaths = {}
    usePrefix = False

    def cache_folder(self, folder, t):
        self.times[folder] = t
        baseFolder = os.path.basename(folder)
        if baseFolder in self.ignoreFolders:
            return
        for dirpath, dirnames, filenames in os.walk(folder):
            if not filenames:
                continue
            filtered = fnmatch.filter(filenames, self.filefilter)
            if filtered:
                for file in filtered:
                    path = "{}/{}".format(dirpath, file)
                    if self.usePrefix:
                        item = sublime.QuickPanelItem(baseFolder + "> " + file, path)
                    else:
                        item = sublime.QuickPanelItem(file, path)
                    self.cachedItems[folder].insert(0, item)
                    self.cachedPaths[folder].insert(0, path)

    def run(self):
        print("goto_file: running the command")
        self.items = []
        self.paths = []
        folders = self.window.folders()

        if len(folders) > 1:
            self.usePrefix = True

        for folder in folders:
            t = os.stat(folder).st_mtime

            if folder in self.times:
                cachedTime = self.times[folder]
                if t != cachedTime:
                    print("goto_file: cache outdated {}:{}".format(cachedTime, t))
                    self.cachedItems[folder] = []
                    self.cachedPaths[folder] = []
                    self.cache_folder(folder, t)
                    for c in self.cachedItems[folder]:
                        self.items.insert(0, c)
                    for c in self.cachedPaths[folder]:
                        self.paths.insert(0, c)
                else:
                    print("goto_file: cache up to date for: ", folder)
                    for c in self.cachedItems[folder]:
                        self.items.insert(0, c)
                    for c in self.cachedPaths[folder]:
                        self.paths.insert(0, c)
                    continue

            else:
                print("goto_file: folder: ", folder," not cached")
                self.times[folder] = t
                self.cachedItems[folder] = []
                self.cachedPaths[folder] = []
                self.cache_folder(folder, t)
                for c in self.cachedItems[folder]:
                    self.items.insert(0, c)
                for c in self.cachedPaths[folder]:
                    self.paths.insert(0, c)

        
        self.window.show_quick_panel(self.items, self.check_selection, self.panelFlags, placeholder= "Enter a Path name")
        print("goto_file: items len: {}".format(len(self.items)))

    def check_selection(self, value):
        if value == -1:
            return
        print("goto_file: selection: {} paths: {} ".format(value, len(self.paths)))
        selected = self.paths[value]
        print("goto_file: open", value, selected)
        self.window.open_file(selected)