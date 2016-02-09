#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import re
import subprocess
import sys
import time

SHELL='/bin/bash'
SOURCE = 'codebender_cc'

class Tests:
    def __init__(self, url, environment):
        self.source=SOURCE
        self.url = url
        self.environment = os.path.abspath(environment)
        self.email = os.getenv('EMAIL', 'void@mail.0')
        self.files_to_ignore = [
            '.gitignore'
        ]

    def run(self, operation, libraries=None):
        if operation == 'common':
            self.common()
        elif operation == 'libraries':
            self.libraries()
        elif operation == 'examples':
            self.examples()
        elif operation == 'sketches':
            self.sketches()
        elif operation == 'compile':
            self.compile(libraries)
        elif operation == 'noplugin':
            self.noplugin()
        elif operation == 'walkthrough':
            self.walkthrough()
        elif operation == 'staging':
            self.staging()

    def run_command(self, command, user_agent=None):
        if user_agent:
            os.environ['SELENIUM_USER_AGENT'] = user_agent
        command = ' '.join(command)
        print('command:', command)
        return subprocess.call(command, shell=True, executable=SHELL)

    def send_mail_no_logs(self, identifier):
        command = ['mail', '-s', '"Selenium Tests: {identifier} Failed To Run" {email} <<< "Something went wrong with {identifier} tests. Please check the logs."'.format(identifier=identifier, email=self.email)]
        run_command(command)

    def send_mail_with_logs(self, identifier):
        default_tests_dir = os.path.normpath(os.path.join(os.getcwd(), '..'))
        root_dir = os.getenv('ROOTDIR', default_tests_dir)

        logs = os.path.join(root_dir, 'logs')
        reports = os.path.join(root_dir, 'reports')
        log_regexp = re.compile('.+{identifier}.+'.format(identifier=identifier))

        try:
            logfile = sorted([filename for filename in os.listdir(logs) if filename not in files_to_ignore and log_regexp.match(filename)], reverse=True)[0]
            logfile_timestamp = re.match(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-.+', logfile).group(1)

            report_regexp = re.compile('report_{timestamp}-{identifier}_(\d+)'.format(timestamp=logfile_timestamp, identifier=identifier))
            reportfile = sorted([filename for filename in os.listdir(reports) if filename not in files_to_ignore and report_regexp.match(filename)], reverse=True)[0]
            changes = report_regexp.match(reportfile).group(1)

            email_date = time.strftime('%Y-%m-%d %H:%M:%S')

            command = [
                '(echo "Changes since the last time: {changes}";'.format(changes=changes),
                'uuencode "{logs}/{logfile}" "{logfile}";'.format(logs=logs, logfile=logfile),
                'uuencode "{reports}/{reportfile}" "{reportfile}")'.format(reports=reports, reportfile=reportfile),
                '| mail -s "Selenium Tests Report: {identifier} {email_date} Changes: {changes}" {email}'.format(identifier=identifier, email_date=email_date, changes=changes, email=self.email)
            ]
            run_command(command)
        except:
            pass

    def create_command(self, test_directory, *extra_arguments):
        return ['tox', 'tests/' + test_directory, '--', '--url={}'.format(TARGETS[self.url]), '--source={}'.format(SOURCE)] + list(extra_arguments)

    def common(self, identifier='common'):
        command = self.create_command('common', '--plugin')
        retval = self.run_command(command)
        if retval != 0:
            self.send_mail_no_logs(identifier)

    def libraries(self, identifier='libraries_fetch'):
        command = self.create_command('libraries_fetch', '-F', '--plugin')
        self.run_command(command)
        self.send_mail_with_logs(identifier)

    def examples(self, identifier='libraries_test'):
        command = self.create_command('libraries', '-F', '--plugin')
        self.run_command(command)
        self.send_mail_with_logs(identifier)

    def sketches(self, libraries, identifier='cb_compile_tester'):
        command = self.create_command('compile_tester', '-F', '--plugin')
        self.run_command(command)
        self.send_mail_with_logs(identifier)

    def compile(self, libraries):
        command = self.create_command('target_libraries', '-F', '--plugin', '--libraries={}'.format(libraries))
        self.run_command(command)

    def noplugin(self, identifier = 'noplugin'):
        command = self.create_command('noplugin')
        retval = self.run_command(command)
        if retval != 0:
            self.send_mail_no_logs(identifier)

    def walkthrough(self, identifier='walkthrough'):
        command = self.create_command('walkthrough', '--plugin')
        retvals = []
        user_agents = [
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium',
            'Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium'
        ]
        for user_agent in user_agents:
            retval = self.run_command(command, user_agent=user_agent)
            retvals.append(retval)
        retval = max(retvals)
        if retval != 0:
            self.send_mail_no_logs(identifier)

    def staging(self):
        command = self.create_command('compile_tester', '-F', '--plugin')
        self.run_command(command)

OPERATIONS = {
    'common':'\tTest site common functionality',
    'libraries': 'Visit all libraries and their examples',
    'examples': 'Compile all examples',
    'sketches': 'Compile sketch of cb_compile_tester user',
    'compile': '\tCompile specific examples',
    'noplugin': 'Run tests without app/plugin installed',
    'walkthrough': 'Run tests for walkthrough',
    'staging': '\tRun tests for staging only'
}

TARGETS = {
    'live': 'https://codebender.cc',
    'staging': 'https://staging.codebender.cc',
    'local': 'http://dev.codebender.cc'
}

def main():
    available_operations = ['{operation}\t{description}'.format(operation=x, description=OPERATIONS[x]) for x in sorted(OPERATIONS.keys())]
    available_targets = ['{target}\t{url}'.format(target=x, url=TARGETS[x]) for x in sorted(TARGETS.keys())]

    parser = argparse.ArgumentParser(description="seleniumbender - A command line tool for codebender's Selenium tests",
                                    epilog='Happy testing :)',
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('operation',
                        help='Operation to execute.\nAvailable operations:\n\t{operations}'.format(operations='\n\t'.join(available_operations)))
    parser.add_argument('--target',
                        default='live',
                        help='Target site for the tests.\nAvailable targets (default: live):\n\t{targets}'.format(targets='\n\t'.join(available_targets)))
    parser.add_argument('--config',
                        default='env_vars.sh',
                        help='Configuration file to load (default: config.cfg).')
    parser.add_argument('--libraries',
                        default=None,
                        help='Libraries to test (comma separated machine names) when using option: target')
    parser.add_argument('--saucelabs',
                        action='store_true',
                        default=False,
                        help='Use saucelabs as the Selenium server')

    # Parse arguments
    args = parser.parse_args()
    operation = args.operation
    if operation not in OPERATIONS:
        print('Unsupported operation!\n')
        parser.print_help()
        sys.exit()

    target = args.target
    if target not in TARGETS:
        print('Unsupported target!\n')
        parser.print_help()
        sys.exit()

    config = args.config
    if not os.path.exists(config):
        print('Config file:', config, 'does not exist')
        sys.exit()

    libraries = args.libraries
    if operation == 'target' and not libraries:
        print('No target libraries specified!\n')
        parser.print_help()
        sys.exit()

    # Read environment variables file
    output = subprocess.check_output('source {}; env'.format(config), shell=True, executable=SHELL)
    env_vars = dict((line.split('=', 1) for line in output.splitlines()))
    os.environ.update(env_vars)

    # Run tests
    tests = Tests(target, config)
    tests.run(operation, libraries=libraries)

if __name__ == '__main__':
    main()