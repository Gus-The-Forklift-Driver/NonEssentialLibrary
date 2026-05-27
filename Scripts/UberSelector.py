# This script generates a PopcornFX template that implements an "uber selector" node.
import pyperclip
import random


def randUUID():
    return ''.join(random.choices('0123456789ABCDEF', k=8))


def _connectedBlock(uuid):
    if not uuid:
        return ''
    return (
        '\n    ConnectedPins = {\n'
        f'        "${uuid}",\n'
        '    };'
    )


def _buildScriptNode(count, script_uuid, selector_pin, comp_pins, in_pins, out_pin,
                     workspace_pos=(-2002, 2486),
                     selector_connected=None, comp_connected=None,
                     in_connected=None, out_connected=None):
    """Build the CParticleNodeScript and its PinIn/PinOut nodes.

    The optional *_connected args are template-export pin UUIDs to wire each
    script pin back to. When omitted the pin has no ConnectedPins (raw node)."""
    code = 'Out = setdim(0*Selector.x, getdim(Selector), 0);\n\n'
    for i in range(count):
        code += f'auto cond{i} = Comp{i} == Selector;\n'
    code += '\n'
    for i in range(count):
        code += f'Out = select(Out, In{i}, cond{i});\n'

    all_input_uuids = [selector_pin] + list(comp_pins) + list(in_pins)
    input_pins_str = '\n'.join(f'            "${u}",' for u in all_input_uuids)

    blocks = []
    blocks.append(
        f'CParticleNodeScript\t${script_uuid}\n'
        '    {\n'
        '        InputPins = {\n'
        f'{input_pins_str}\n'
        '        };\n'
        '        OutputPins = {\n'
        f'            "${out_pin}",\n'
        '        };\n'
        f'        WorkspacePosition = int2({workspace_pos[0]}, {workspace_pos[1]});\n'
        f'        Expression = "{code}";\n'
        '    }'
    )

    blocks.append(
        f'CParticleNodePinIn\t${selector_pin}\n'
        '    {\n'
        '        SelfName = "Selector";\n'
        f'        Owner = "${script_uuid}";{_connectedBlock(selector_connected)}\n'
        '    }'
    )

    for i, u in enumerate(comp_pins):
        conn = comp_connected[i] if comp_connected else None
        blocks.append(
            f'CParticleNodePinIn\t${u}\n'
            '    {\n'
            f'        SelfName = "Comp{i}";\n'
            f'        Owner = "${script_uuid}";{_connectedBlock(conn)}\n'
            '    }'
        )

    for i, u in enumerate(in_pins):
        conn = in_connected[i] if in_connected else None
        blocks.append(
            f'CParticleNodePinIn\t${u}\n'
            '    {\n'
            f'        SelfName = "In{i}";\n'
            f'        Owner = "${script_uuid}";{_connectedBlock(conn)}\n'
            '    }'
        )

    blocks.append(
        f'CParticleNodePinOut\t${out_pin}\n'
        '    {\n'
        '        SelfName = "Out";\n'
        f'        Owner = "${script_uuid}";{_connectedBlock(out_connected)}\n'
        '    }'
    )

    return '\n    '.join(blocks)


def makeUberSelectorScript(count):
    """Generate just the script node (no surrounding template exports)."""
    script_uuid = '589D2D30'
    selector_pin = '5464A2E3'
    out_pin = 'AAD535CC'
    comp_pins = [randUUID() for _ in range(count)]
    in_pins = [randUUID() for _ in range(count)]

    body = _buildScriptNode(count, script_uuid, selector_pin,
                            comp_pins, in_pins, out_pin)

    return (
        'PKFX\n'
        '    File = NonEssentialLibrary/Templates.pkfx\n'
        '    Version = 2.24.2.26533;\n'
        f'    {body}\n'
        '\n'
        '    '
    )


def _inputExport(uuid, in_pin, out_pin, name, x, y, connect_to,
                 rule_index=None):
    """A standard typed input template export (Selector / CompN / InN)."""
    if rule_index is not None:
        rule_value = f'\n        RuleValue = "{rule_index}";' if rule_index > 0 else ''
        rule_block = (
            '\n        PinRules = Rule1;'
            '\n        BaseVisibility = Hidden;'
            '\n        RuleResult = Visible;'
            '\n        DependentProperty = "InputCount";'
            '\n        RuleFunction = Greater;'
            f'{rule_value}'
        )
    else:
        rule_block = ''

    return (
        f'CParticleNodeTemplateExport\t${uuid}\n'
        '{\n'
        '    InputPins = {\n'
        f'        "${in_pin}",\n'
        '    };\n'
        '    OutputPins = {\n'
        f'        "${out_pin}",\n'
        '    };\n'
        f'    WorkspacePosition = int2({x}, {y});\n'
        f'    ExportedName = "{name}";\n'
        '    ExportedTypeMask = 8190;\n'
        f'    Type = Input;'
        f'DefaultValueF4 = float4({rule_index}.0000000e+00, {rule_index}.0000000e+00, {rule_index}.0000000e+00, {rule_index}.0000000e+00);\n'
        f'DefaultValueI4 = int4({rule_index}, {rule_index}, {rule_index}, {rule_index});\n'
        f'{rule_block}\n'
        '}\n'
        f'CParticleNodePinIn\t${in_pin}\n'
        '{\n'
        '    SelfName = "DefaultValue";\n'
        '    Visible = false;\n'
        f'    Owner = "${uuid}";\n'
        '}\n'
        f'CParticleNodePinOut\t${out_pin}\n'
        '{\n'
        '    SelfName = "Value";\n'
        f'    Owner = "${uuid}";'
        f'{_connectedBlock(connect_to)}\n'
        '}'
    )


def _inputCountExport(uuid, in_pin, out_pin, x, y, max_count):
    """The int-slider InputCount export that drives the visibility rules."""
    return (
        f'CParticleNodeTemplateExport\t${uuid}\n'
        '{\n'
        '    InputPins = {\n'
        f'        "${in_pin}",\n'
        '    };\n'
        '    OutputPins = {\n'
        f'        "${out_pin}",\n'
        '    };\n'
        f'   WorkspacePosition = int2({x}, {y});\n'
        '    ExportedName = "InputCount";\n'
        '    ExportedType = int;\n'
        '    Type = Input;\n'
        '    HasMin = true;\n'
        '    HasMax = true;\n'
        '    UseSlider = true;\n'
        '    DefaultValueI4 = int4(2, 2, 2, 2);\n'
        '    MinValueI4 = int4(2, 2, 2, 2);\n'
        f'    MaxValueI4 = int4({max_count}, {max_count}, {max_count}, {max_count});\n'
        '}\n'
        f'CParticleNodePinIn\t${in_pin}\n'
        '{\n'
        '    SelfName = "DefaultValue";\n'
        '    Visible = false;\n'
        f'    Owner = "${uuid}";\n'
        '}\n'
        f'CParticleNodePinOut\t${out_pin}\n'
        '{\n'
        '    SelfName = "Value";\n'
        '    Visible = false;\n'
        f'    Owner = "${uuid}";\n'
        '}'
    )


def _outputExport(uuid, in_pin, x, y, connect_to):
    """The Out template export (Type = Output, single input pin)."""
    return (
        f'CParticleNodeTemplateExport\t${uuid}\n'
        '    {\n'
        '        InputPins = {\n'
        f'            "${in_pin}",\n'
        '        };\n'
        f'        WorkspacePosition = int2({x}, {y});\n'
        '        ExportedName = "Out";\n'
        '        Type = Output;\n'
        '    }\n'
        f'    CParticleNodePinIn\t${in_pin}\n'
        '    {\n'
        '        SelfName = "Value";\n'
        f'        Owner = "${uuid}";'
        f'{_connectedBlock(connect_to)}\n'
        '    }'
    )


def makeUberSelectorTemplate(count):
    """Generate the complete template graph: Selector + InputCount + N*(Comp,In)
    + script node + Out, all wired up. `count` becomes the max InputCount."""
    # script-side UUIDs
    script_uuid = randUUID()
    selector_pin = randUUID()
    out_pin = randUUID()
    comp_pins = [randUUID() for _ in range(count)]
    in_pins = [randUUID() for _ in range(count)]

    # template-export UUIDs: (export, input_pin, output_pin)
    sel_exp = (randUUID(), randUUID(), randUUID())
    ic_exp = (randUUID(), randUUID(), randUUID())
    comp_exps = [(randUUID(), randUUID(), randUUID()) for _ in range(count)]
    in_exps = [(randUUID(), randUUID(), randUUID()) for _ in range(count)]
    out_exp = (randUUID(), randUUID())  # only an input pin

    script_body = _buildScriptNode(
        count, script_uuid, selector_pin, comp_pins, in_pins, out_pin,
        workspace_pos=(-990, 3454),
        selector_connected=sel_exp[2],
        comp_connected=[e[2] for e in comp_exps],
        in_connected=[e[2] for e in in_exps],
        out_connected=out_exp[1],
    )

    blocks = []
    blocks.append(_inputCountExport(ic_exp[0], ic_exp[1], ic_exp[2],
                                    -1430, 3300, max_count=count))
    blocks.append(_inputExport(sel_exp[0], sel_exp[1], sel_exp[2],
                               "Selector", -1430, 3454,
                               connect_to=selector_pin))

    y = 3586
    for i, exp in enumerate(comp_exps):
        blocks.append(_inputExport(exp[0], exp[1], exp[2],
                                   f"Compare Value {i}", -1430, y,
                                   connect_to=comp_pins[i], rule_index=i))
        y += 132
    for i, exp in enumerate(in_exps):
        blocks.append(_inputExport(exp[0], exp[1], exp[2],
                                   f"Input {i}", -1430, y,
                                   connect_to=in_pins[i], rule_index=i))
        y += 132

    blocks.append(script_body)
    blocks.append(_outputExport(out_exp[0], out_exp[1],
                                -594, 3454, connect_to=out_pin))

    body = '\n    '.join(blocks)
    return (
        'PKFX\n'
        'File = NonEssentialLibrary/Templates.pkfx\n'
        'Version = 2.24.2.26533;\n'
        f'{body}\n'
        '\n'
        '    '
    )


if __name__ == '__main__':
    template = makeUberSelectorTemplate(count=256)
    pyperclip.copy(template)
