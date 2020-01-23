import requests
import json
import argparse


def get_parameters():
    parser = argparse.ArgumentParser(description='Enter --url and --token')
    parser.add_argument('url', help='Gitlab api URL')
    parser.add_argument('token', help='Gitlab user token id')
    return parser.parse_args()


def gitlab_jobs_status(tokenid, gitlab_url):
    print("Executing...")
    projects = requests.get(
        '%s/api/v4/projects?per_page=100' % gitlab_url,
        headers={'Private-Token': tokenid})

    projects_list = json.loads(projects.text)

    running_jobs = 0
    pending_jobs = 0
    runners = {}
    # get all projects
    for project in projects_list:
        jobs = requests.get(
            '%s/api/v4/projects/%s/jobs?scope[]=pending&scope[]=running&per_page=100' % (gitlab_url, project['id']),
            headers={'Private-Token': tokenid})
        jobs_list = json.loads(jobs.text)
        # get all jobs in each project
        for job in jobs_list:
            print("Project: %s" % (project['path_with_namespace']))
            print("  Pipeline: %s" % (job['status']))
            if job['status'] == 'pending':
                pending_jobs += 1
            elif job['status'] == 'running':
                running_jobs += 1
                print("  Runner name: %s" % (job['runner']['description']))
                try:
                    runners[job['runner']['description']]
                except KeyError:
                    runners = {job['runner']['description']: 1}
                else:
                    runners = {job['runner']['description']: runners.get(job['runner']['description'])+1}
            else:
                print('Please check project status')
    print(80*'-')
    for runner in runners:
        print("Runner %s has %s jobs" % (runner, runners[runner]))
    print(80*'-')
    print('Summary:')
    print('  Running jobs: %s' % running_jobs)
    print('  Pending jobs: %s' % pending_jobs)
    return running_jobs, pending_jobs


if __name__ == '__main__':
    args = get_parameters()
    gitlab_jobs_status(args.token, args.url)
