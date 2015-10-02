import os
import re


class TranslationFileFinder(object):

    path_mapping = (
        (".", "\."),
        ("<lang>", "(?P<lang>[\w]*)"),
        ("<filename>", "(?P<filename>[\w]*)"),
        ("<directory_path>", "(?P<directory_path>[\w\/]*?)"))

    def __init__(self, translation_path):
        self.translation_path = translation_path
        self.validate_path()
        self.regex = re.compile(self._parse_path())

    @property
    def file_root(self):
        file_root = self.translation_path.split("<")[0]
        if not file_root.endswith("/"):
            file_root = "/".join(file_root.split("/")[:-1])
        return file_root.rstrip("/")

    def find(self):
        for root, dirs, files in os.walk(self.file_root):
            for filename in files:
                file_path = os.path.join(root, filename)
                match = self.match(file_path)
                if match:
                    matched = match.groupdict()
                    matched["directory_path"] = (
                        matched.get("directory_path", "").strip("/"))
                    if matched.get("filename"):
                        matched["filename"] = (
                            "%s%s"
                            % (matched["filename"],
                               os.path.splitext(file_path)[1]))
                    yield file_path, matched

    def match(self, file_path):
        return self.regex.match(file_path)

    def _parse_path(self):
        path = self.translation_path
        for k, v in self.path_mapping:
            path = path.replace(k, v)
        return "%s$" % path

    def validate_path(self):
        path = self.translation_path
        links_to_parent = (
            path == ".."
            or path.startswith("../")
            or "/../" in path
            or path.endswith("/.."))

        if links_to_parent:
            raise ValueError(
                "Translation path should not contain '..'")

        if "<lang>" not in path:
            raise ValueError(
                "Translation path must contain a <lang> pattern to match.")

        stripped_path = (path.replace("<lang>", "")
                             .replace("<directory_path>", "")
                             .replace("<filename>", ""))

        if "<" in stripped_path or ">" in stripped_path:
            raise ValueError(
                "Only <lang>, <directory_path> and <filename> are valid "
                "patterns to match in the translation path")

        if re.search("[^\w\/\-\.]+", stripped_path):
            raise ValueError(
                "Translation paths can only contain alpha-numeric characters, "
                "_ or -: '%s'" % path)
