from os import path
import re

import click
from lxml import etree

POLARION_PROJECT_ID = 'CNV'


class Element:
    def __init__(self, tag, attributes):
        self.tag = tag
        self.attributes = attributes


def add_children(parent, children):
    added_children = []
    for child in children:
        added_children.append(etree.SubElement(parent, child.tag, child.attributes))
    return added_children


def remove_login_testsuite(root):
    """
    Every openshift/console test suite starts with authentication and creates a new test namespace
    These tests are included in the test report, as prerequisites for the remaining tests, however
    not part of the actual test suite.
    """
    login_nodes = root.xpath(
        "//testsuite[contains(@name,  'Auth test')  or  contains(@name,  'Create a test namespace')]"
    )
    for login_node in login_nodes:
        login_node.getparent().remove(login_node)


def add_testsuites_properties(xml, custom_plannedin, tier, env_storage, env_os, dry_run):
    properties = [
        Element('property', {'name': 'polarion-project-id', 'value': POLARION_PROJECT_ID}),
        Element('property', {'name': 'polarion-lookup-method', 'value': 'id'}),
        Element('property', {'name': 'polarion-custom-plannedin', 'value': custom_plannedin}),
        Element(
            'property',
            {
                'name': 'polarion-testrun-id',
                'value': '_'.join([custom_plannedin, tier, env_storage, env_os])
            }
        ),
        Element('property', {'name': 'polarion-custom-isautomated', 'value': 'True'}),
        Element('property', {'name': 'polarion-testrun-status-id', 'value': 'inprogress'}),
        Element('property', {'name': 'polarion-custom-env-os', 'value': 'inprogress'}),
        Element('property', {'name': 'polarion-custom-env-storage', 'value': 'inprogress'}),
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
        else:
            raise Exception("Couldn't find test case identifier in '{}'".format(
                testcase.get('name')
            ))


@click.command()
@click.option('--report-path', help='path to the XML file with tests report', required=True)
@click.option(
    '--custom-plannedin',
    help='planned in attribute used for polarion-custom-plannedin. Example: 2_3',
    required=True)
@click.option(
    '--tier',
    help='tier of the test run',
    type=click.Choice(['tier1', 'tier2', 'tier3'], case_sensitive=False),
    required=True
)
@click.option('--env-storage', help='storage class used for the test run', required=True)
@click.option('--env-os', help='OS used on cluster nodes', default='RHCOS', show_default=True)
@click.option(
    '--dry-run',
    help='use True for dry run, False by default',
    type=click.Choice(['True', 'False'], case_sensitive=False),
    default='False',
    show_default=True
)
def main(report_path, custom_plannedin, tier, env_storage, env_os, dry_run):
    xml = etree.parse(report_path)

    # Remove authentication cases
    remove_login_testsuite(xml)

    # add and process testcase properties
    testcases = xml.xpath("//testcase")
    process_testcases(testcases)

    # add test suite properties
    add_testsuites_properties(xml, custom_plannedin, tier, env_storage, env_os, dry_run)

    # write the result to a file
    basepath, filename = path.split(report_path)
    with open(path.join(basepath, 'processed-{}'.format(filename)), 'wb+') as fd:
        fd.write(etree.tostring(xml, pretty_print=True))


if __name__ == '__main__':
    main()
