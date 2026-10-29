"""Consumer-owned ProcessOrders definition; agent implementation is deliberately absent."""
from boundscript_internal.box_definition import BoxDefinition, VerificationSuite

BOX = BoxDefinition(
    name='process-orders-native',
    task_path='task.md',
    contract_path='src/contract.ts',
    contract_module='/implementation/contract.ts',
    function_type='ProcessOrders',
    implementation_export='processOrders',
    accepted_path='accepted/process-orders.ts',
    verification_path='.',
    suites=(
        VerificationSuite(('runtime',), ('validators.test.ts',)),
        VerificationSuite(('acceptance', 'properties'), ('acceptance.test.ts',)),
    ),
    verification_inputs=('src', '.generated/contract.ts', '.generated/validators.ts',
                         'fixtures/order-cases.json'),
)
