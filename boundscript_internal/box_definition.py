"""Explicit native Box inputs; no source inference, registry or acceptance oracle."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import PurePosixPath
import re

from boundscript_internal.typescript_contract import generate_contract_check


CATEGORIES = frozenset(('runtime', 'acceptance', 'properties'))
TEST_FILE = re.compile(r'.+\.(?:test|spec)\.(?:[jt]sx?|[cm][jt]s)$')


def verification_relative_path(value):
    """Literal relative paths only, not globs, CLI options or traversal."""
    if (not isinstance(value, str) or not value or
            any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..')
                for part in value.split('/')) or PurePosixPath(value).is_absolute()):
        raise ValueError('Expected a literal relative verification path')
    return value


@dataclass(frozen=True)
class VerificationSuite:
    categories: tuple[str, ...]
    files: tuple[str, ...]


@dataclass(frozen=True)
class BoxDefinition:
    name: str
    task_path: str
    contract_path: str
    contract_module: str
    function_type: str
    implementation_export: str
    accepted_path: str
    verification_path: str
    suites: tuple[VerificationSuite, ...] = ()
    verification_inputs: tuple[str, ...] = ()
    optional_categories: tuple[str, ...] = ()

    def verification_files(self, root):
        """Validate complete test ownership; return only explicitly staged inputs.

        Every *.test/spec JS/TS file under the Box's verification root must belong
        to exactly one suite. Optional means absent/not applicable, never skipped
        tests. Runtime validation and acceptance are always mandatory.
        """
        if root.is_symlink() or not root.is_dir():
            raise ValueError('Expected a regular verification directory')
        optional = set(self.optional_categories)
        if (len(optional) != len(self.optional_categories) or optional - {'properties'}):
            raise ValueError('Only properties may be explicitly not applicable')
        categories, declared = set(), []
        for suite in self.suites:
            if (not suite.categories or not suite.files or
                    len(set(suite.categories)) != len(suite.categories) or
                    set(suite.categories) - CATEGORIES):
                raise ValueError('Expected nonempty verification suite categories and files')
            categories.update(suite.categories)
            declared.extend(verification_relative_path(file) for file in suite.files)
        if categories & optional or categories | optional != CATEGORIES:
            raise ValueError('Every verification category must be required or explicitly not applicable')
        if len(set(declared)) != len(declared):
            raise ValueError('Each test file must belong to exactly one suite')
        inventory = set()
        for path in root.rglob('*'):
            if path.is_symlink():
                raise ValueError('Verification inputs must not contain symlinks')
            if path.is_file() and TEST_FILE.fullmatch(path.name):
                inventory.add(path.relative_to(root).as_posix())
        if set(declared) != inventory:
            raise ValueError('Declared tests must exactly cover the verification directory test files')
        files = set(declared)
        for value in self.verification_inputs:
            path = root / verification_relative_path(value)
            if not path.exists() or path.is_symlink():
                raise ValueError('Missing or unsafe verification input')
            if path.is_file():
                files.add(value)
            else:
                files.update(p.relative_to(root).as_posix() for p in path.rglob('*') if p.is_file())
        for file in files:
            verification_relative_path(file)
        return tuple(sorted(files))

    def contract_check(self, implementation_module):
        return generate_contract_check(self.contract_module, self.function_type,
                                       implementation_module, self.implementation_export)

    def fingerprint(self):
        """Bind separate generation/verification processes to identical settings."""
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True,
                                         separators=(',', ':')).encode()).hexdigest()
