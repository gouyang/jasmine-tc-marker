# jasmine-tc-marker

Tool for processing Jasmine XML test report.

__Dependencies__

- click
- lxml


__What does it do__

The following is snippet taken from Jasmine XML reporter:
```xml
<testsuite name="CNV Installation" timestamp="2020-04-16T23:28:05" hostname="localhost" time="232.139" errors="0" tests="2" skipped="0" disabled="0" failures="0">
    <testcase classname="CNV Installation" name="ID(CNV-3822) Install CNV Operator" time="64.041"/>
    <testcase classname="CNV Installation" name="ID(CNV-4003) Deploys HyperConverged Cluster" time="79.516"/>
</testsuite>
```

will look like:
```xml
 <testsuite name="CNV Installation" timestamp="2020-04-16T23:28:05" hostname="localhost" time="232.139" errors="0" tests="2" skipped="0" disabled="0" failures="0">
  <testcase classname="CNV Installation" name="Install CNV Operator" time="64.041">
    <properties>
        <property name="polarion-testcase-id" value="CNV-3822"/>
    </properties>
  </testcase>
  <testcase classname="CNV Installation" name="Deploys HyperConverged Cluster" time="79.516">
    <properties>
      <property name="polarion-testcase-id" value="CNV-4003"/>
    </properties>
  </testcase>
 </testsuite>

```


__Usage__


```console
Usage: cli.py [OPTIONS]

Options:
  --report-path TEXT          path to the XML file with tests report
                              [required]

  --custom-plannedin TEXT     planned in attribute used for polarion-custom-
                              plannedin. Example: 2_3  [required]

  --tier [tier1|tier2|tier3]  tier of the test run  [required]
  --env-storage TEXT          storage class used for the test run  [required]
  --env-os TEXT               OS used on cluster nodes  [default: RHCOS]
  --dry-run [True|False]      use True for dry run  [default: False]

  --help                      Show this message and exit.

```


__Example__

`python cli.py --report-path ./test-report.xml --custom-plannedin=2_3 --tier=tier1 --env-storage=nfs`