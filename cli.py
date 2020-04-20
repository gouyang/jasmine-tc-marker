from os import path
import re

import click
from lxml import etree


class Element:
    def __init__(self, tag, attributes):
        self.tag = tag
        self.attributes = attributes


def add_children(parent, children):
    added_children = []
    for child in children:
        added_children.append(etree.SubElement(parent, child.tag, child.attributes))
    return added_children


def add_testsuites_properties(xml, project_id, plannedin, tier, env_storage, env_os, dry_run):
    properties = [
        Element('property', {'name': 'polarion-project-id', 'value': project_id}),
        Element('property', {'name': 'polarion-lookup-method', 'value': 'id'}),
        Element('property', {'name': 'polarion-custom-plannedin', 'value': plannedin}),
        Element(
            'property',
            {
                'name': 'polarion-testrun-id',
                'value': '_'.join([plannedin, tier, env_os, env_storage])
            }
        ),
        Element('property', {'name': 'polarion-custom-isautomated', 'value': 'True'}),
        Element('property', {'name': 'polarion-testrun-status-id', 'value': 'inprogress'}),
        Element('property', {'name': 'polarion-custom-env-os', 'value': env_os}),
        Element('property', {'name': 'polarion-custom-env-storage', 'value': env_storage}),
        Element('property', {'name': 'polarion-dry-run', 'value': dry_run}),
    ]
    testsuites_properties = etree.SubElement(xml.getroot(), 'properties')
    add_children(testsuites_properties, properties)


def process_testcases(testcases):
    regex = re.compile(r'ID\(CNV-\d+\)\s*')
    for testcase in testcases:
        found = regex.search(testcase.get('name'))
        if found:
            testcase_id = found.group(0).strip()[3:-1]
            testcase_properties = etree.SubElement(testcase, 'properties')
            add_children(
                testcase_properties,
                [Element('property', {'name': 'polarion-testcase-id', 'value': testcase_id})]
            )
            # Remove the identifier from the testcase name
            testcase.set('name', regex.sub('', testcase.get('name')))


@click.command()
@click.option('--report-path', help='path to the XML file with tests report', required=True)
@click.option(
    '--polarion-project',
    help='Polarion project indentifier',
    default='CNV',
    show_default=True,
)
@click.option(
    '--custom-plannedin',
    help='planned in attribute used for polarion-custom-plannedin.',
    default='2_3',
    show_default=True
)
@click.option(
    '--tier',
    help='tier of the test run',
    type=click.Choice(['tier1', 'tier2', 'tier3'], case_sensitive=False),
    default='tier1',
    show_default=True,
)
@click.option('--env-storage', help='storage class used for the test run', default='nfs', show_default=True)
@click.option('--env-os', help='OS used on cluster nodes', default='RHCOS', show_default=True)
@click.option(
    '--dry-run',
    help='use True for dry run, False by default',
    type=click.Choice(['True', 'False'], case_sensitive=False),
    default='False',
    show_default=True,
)
def main(report_path, polarion_project, custom_plannedin, tier, env_storage, env_os, dry_run):
    xml = etree.parse(report_path)

    # add test suite properties
    add_testsuites_properties(xml, polarion_project, custom_plannedin, tier, env_storage, env_os, dry_run)

    # add and process testcase properties
    testcases = xml.xpath("//testcase")
    process_testcases(testcases)

    # write the result to a file
    basepath, filename = path.split(report_path)
    with open(path.join(basepath, 'processed-{}'.format(filename)), 'wb+') as fd:
        fd.write(etree.tostring(xml, pretty_print=True))


if __name__ == '__main__':
    main()
