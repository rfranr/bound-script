"""Consumer-owned PlanFulfillment specification and verification bundle."""
from boundscript_internal.box_definition import BoxDefinition, VerificationSuite

BOX = BoxDefinition(
    name='plan-fulfillment-native',
    task_path='task.md',
    contract_path='src/contract.ts',
    contract_module='/implementation/contract.ts',
    function_type='PlanFulfillment',
    implementation_export='planFulfillment',
    accepted_path='accepted/plan-fulfillment.ts',
    verification_path='.',
    suites=(
        VerificationSuite(('runtime',), ('validators.test.ts',)),
        VerificationSuite(('acceptance', 'properties'), ('acceptance.test.ts',)),
    ),
    verification_inputs=('src', '.generated/contract.ts', '.generated/validators.ts',
                         'fixtures/fulfillment-cases.json'),
)
