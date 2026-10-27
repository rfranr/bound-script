"""Fixed RenderWelcome inputs and independently owned verification bundle.

All paths are relative to this Box root, never a peer experiment.
"""
from boundscript_internal.box_definition import BoxDefinition, VerificationSuite

BOX = BoxDefinition(
    name='render-welcome-native',
    task_path='task.md',
    contract_path='src/contract.ts',
    contract_module='/inputs/contract.ts',
    function_type='RenderWelcome',
    implementation_export='renderWelcome',
    accepted_path='accepted/render-welcome.ts',
    verification_path='.',
    suites=(
        VerificationSuite(('runtime',), ('validators.test.ts',)),
        VerificationSuite(('acceptance', 'properties'), ('acceptance.test.ts',)),
    ),
    verification_inputs=('src', '.generated/contract.ts', '.generated/validators.ts',
                         'fixtures/welcome-cases.json'),
)
