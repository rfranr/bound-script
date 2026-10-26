// Frozen integration: no adaptation, defaults, coercion, cloning or repair.
export async function wire(verifyBoxImplementation, normalizeSpec, normalize, renderSpec, render, input) {
    const intermediate = await verifyBoxImplementation(normalizeSpec, normalize, input);
    if (!intermediate.ok) return { stage: 'normalize', result: intermediate };
    const result = await verifyBoxImplementation(renderSpec, render, intermediate.output);
    return { stage: 'render', intermediate: intermediate.output, result };
}
