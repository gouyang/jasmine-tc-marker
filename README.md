# jasmine-tc-marker

Tool for processing Jasmine XML test report. The script takes an Jasmine XML report and adds property tags for 
test cases which have an ID(PROJECT-IDENTIFIER) label in their name.



__Dependencies__

- click
- lxml


__What does it do__

The following is snippet taken from Jasmine XML reporter:
```xml
<testsuites disabled="0" errors="0" failures="0" tests="17" time="473215">
    <testsuite name="CNV Installation" timestamp="2020-04-16T23:28:05" hostname="localhost" time="232.139" errors="0" tests="1" skipped="0" disabled="0" failures="0">
        <testcase classname="CNV Installation" name="ID(CNV-3822) Install CNV Operator" time="64.041"/>
    </testsuite>
</testsuites>

```

will look like:
```xml
 <testsuites disabled="0" errors="0" failures="0" tests="17" time="473215">
     <testsuite name="CNV Installation" timestamp="2020-04-16T23:28:05" hostname="localhost" time="232.139" errors="0" tests="1" skipped="0" disabled="0" failures="0">
        <testcase classname="CNV Installation" name="Install CNV Operator" time="64.041">
            <properties>
                <property name="polarion-testcase-id" value="CNV-3822"/>
            </properties>
        </testcase>
     </testsuite>
     <properties>
        <property name="polarion-project-id" value="CNV"/>
     </properties>
 </testsuites>

```
For each `<testcase>`, there is added property with `polarion-project-id`, so that Polarion is able to match the test
case with related test case in its database.
Additionally, there are added properties for the entire `<testsuites>` tree, representing the test run.
These properties can be configured in a `.yaml` configuration file. See `cnv-ui-tests-tier2.yaml` for example.


__Usage__


```console
Usage: cli.py [OPTIONS]

Options:
  --report-path TEXT  path to the XML file with tests report  [required]
  --config-file TEXT  path to configuration file  [required]
  --help 
```


__Example__

`python cli.py --report-path ./test-report.xml --config-file ./cnv-ui-tests-tier2.yaml`