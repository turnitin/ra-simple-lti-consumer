# Instructions -- see README.md in this directory
import argparse
import re

import lti
import requests


def consume():
    parser = argparse.ArgumentParser()
    parser.add_argument('--context_id', help='Context (class) identifier, arbitrary', required=True)
    parser.add_argument('--email', help='User email')
    parser.add_argument('--env', help='Environment', default='staging')
    parser.add_argument('--first', help='User first name', required=True)
    parser.add_argument('--key', help='Consumer key', required=True)
    parser.add_argument('--last', help='User last name', required=True)
    parser.add_argument('--resource_link_id', help='Resource link (assignment) identifier, arbitrary', required=True)
    parser.add_argument('--role', help='Role, either "Learner" or "Instructor"', default='Instructor')
    parser.add_argument('--secret', help='Consumer secret', required=True)
    parser.add_argument('--user_id', help='User ID, arbitrary', required=True)
    args = parser.parse_args()

    launch_params = {
        'context_id': args.context_id,
        'context_title': 'A test class',
        'lis_person_contact_email_primary': args.email,
        'lis_person_name_family': args.last,
        'lis_person_name_given': args.first,
        'resource_link_id': args.resource_link_id,
        'resource_link_title': 'A test assignment',
        'roles': args.role,
        'tool_consumer_info_product_family_code': 'ra-test',
        'tool_consumer_info_version': '0.01',
        'tool_consumer_instance_description': 'RA test consumer',
        'tool_consumer_instance_guid': 'www.revisionassistant.com',
        'user_id': args.user_id,
    }

    if args.env == 'staging':
        launch_url = 'https://staging.tiiscoringengine.com/lti/1p0/launch'
    elif args.env == 'production':
        launch_url = 'https://api.tiiscoringengine.com/lti/1p0/launch'
    else:
        launch_url = 'https://{}.getlightbox.com/lti/1p0/launch'.format(args.env)

    tool_consumer = lti.ToolConsumer(
        args.key, args.secret, params=launch_params, launch_url=launch_url)
    launch_request = tool_consumer.generate_launch_request()
    response = requests.post(
        launch_request.url,
        headers=launch_request.headers, data=launch_request.body,
        allow_redirects=False, verify=False)
    print("Status: {}".format(response.status_code))
    if response.status_code == 302:
        for header in sorted(response.headers):
            print("  {}: {}".format(header, response.headers[header]))
        if 'Location' in response.headers:
            print(response.headers['Location'])
        else:
            pat = re.compile('href="([^"]+)"')
            matches = pat.search(response.text)
            if matches:
                print(matches.group(1))
            else:
                print("Failed to find link in body\n{}".format(response.text))
    else:
        # RA will generate an HTML page with a link in it; we'll pull that link out
        # and display it so you can copy-and-paste
        pat = re.compile('action="([^"]+)"')
        matches = pat.search(response.text)
        if matches:
            print(matches.group(1))
        else:
            print("Failed to find link in response text! Status: {}\n{}".format(response.status_code, response.text))


if __name__ == '__main__':
    consume()
