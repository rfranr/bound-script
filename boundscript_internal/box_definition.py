"""Explicit native Box inputs; no discovery, registry or acceptance oracle."""
from dataclasses import asdict, dataclass
import hashlib
import json

from boundscript_internal.typescript_contract import generate_contract_check


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

    def contract_check(self, implementation_module):
        return generate_contract_check(self.contract_module, self.function_type,
                                       implementation_module, self.implementation_export)

    def fingerprint(self):
        """Bind separate generation/verification processes to identical settings."""
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True,
                                         separators=(',', ':')).encode()).hexdigest()
