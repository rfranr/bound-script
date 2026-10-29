"""Consumer-owned EvaluateRules contract and independent verification inputs."""
from boundscript_internal.box_definition import BoxDefinition, VerificationSuite

BOX = BoxDefinition(
    name='evaluate-rules-native',
    task_path='task.md',
    contract_path='src/contract.ts',
    contract_module='/implementation/contract.ts',
    function_type='EvaluateRules',
    implementation_export='evaluateRules',
    accepted_path='accepted/evaluate-rules.ts',
    verification_path='.',
    suites=(
        VerificationSuite(('runtime',), ('validators.test.ts',)),
        VerificationSuite(('acceptance', 'properties'), ('acceptance.test.ts',)),
    ),
    verification_inputs=('src', '.generated/contract.ts', '.generated/validators.ts',
                         'fixtures/rule-cases.json'),
)
