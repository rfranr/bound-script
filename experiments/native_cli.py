#!/usr/bin/env python3
"""Explicit experiment selection, separate from shared workflow functions."""
from importlib import import_module
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from boundscript_internal import native_cli, native_generator, native_promotion


def select_box(selection):
    # Fixed lazy imports, never arbitrary module loading or peer discovery.
    if selection == 'normalize-contact':
        configuration = import_module('experiments.native-typescript-contracts.native_box')
        return ROOT / 'experiments/native-typescript-contracts', configuration.BOX, configuration.BASELINE_SOURCE
    if selection == 'render-welcome':
        configuration = import_module('experiments.render-welcome-native.native_box')
        return ROOT / 'experiments/render-welcome-native', configuration.BOX, None
    if selection == 'process-orders':
        configuration = import_module('experiments.process-orders-native.native_box')
        return ROOT / 'experiments/process-orders-native', configuration.BOX, None
    if selection == 'evaluate-rules':
        configuration = import_module('experiments.evaluate-rules-native.native_box')
        return ROOT / 'experiments/evaluate-rules-native', configuration.BOX, None
    if selection == 'plan-fulfillment':
        configuration = import_module('experiments.plan-fulfillment-native.native_box')
        return ROOT / 'experiments/plan-fulfillment-native', configuration.BOX, None

    raise ValueError('Expected explicit Box: normalize-contact or render-welcome')


def verification_command(selection):
    return [sys.executable, '-B', str(Path(__file__).resolve()), 'verify', selection]


def main(args=None):
    args = sys.argv[1:] if args is None else args
    if len(args) < 2 or args[0] not in ('generate', 'verify', 'promote'):
        print('Usage: python3 -B experiments/native_cli.py {generate|verify|promote} '
              '<box> [--candidate ID for promote; --agent-owned [--retain-candidate] for generate; verification arguments for verify]', file=sys.stderr)
        return 1
    operation, selection = args[:2]
    try:
        root, box, baseline = select_box(selection)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    if operation == 'promote':
        return native_promotion.cli(args[2:], box_root=root, box=box)
    if operation == 'verify':
        return native_cli.cli(args[2:], box_root=root, box=box, baseline_source=baseline)
    return native_generator.cli(box_root=root, box=box,
                                verification_command=verification_command(selection),
                                detailed_diagnostics=selection == 'render-welcome', args=args[2:])


if __name__ == '__main__':
    sys.exit(main())
