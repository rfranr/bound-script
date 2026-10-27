"""Human-selected native Box configuration shared by both entry points.

Paths are relative to this experiment. verification_path owns the independent
acceptance suite, src validators and generated Typia validators, not agent inputs.
"""
from boundscript_internal.box_definition import BoxDefinition

BOX = BoxDefinition(
    name='normalize-contact-native',
    task_path='task.md',
    contract_path='src/contract.ts',
    contract_module='/inputs/contract.ts',
    function_type='NormalizeContact',
    implementation_export='normalizeContact',
    accepted_path='accepted/normalize-contact.ts',
    verification_path='.',
)

# Explicit historical comparison only; not a native contract/Box selection.
BASELINE_SOURCE = '../minimal-box/two-boxes/accepted/normalize-contact.ts'
