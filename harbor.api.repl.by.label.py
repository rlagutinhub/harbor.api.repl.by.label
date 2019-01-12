#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
 
 
# ----------------------------------------------------------------------------------------------------
# NAME:   HARBOR.API.REPL.BY.LABEL.PY
# DESC:   CHECK NEW IMAGES IN REPO WITH ASSIGNED LABEL(S) AND START REPLICATION IF REQURED
# DATE:   31-12-2018
# LANG:   PYTHON 3
# AUTHOR: LAGUTIN R.A.
# EMAIL:  RLAGUTIN@MTA4.RU
# ----------------------------------------------------------------------------------------------------
# Harbor Rest API
 
# http://editor.swagger.io/
# https://raw.githubusercontent.com/goharbor/harbor/master/docs/swagger.yaml
# https://community.pivotal.io/s/article/How-to-Browse-and-Query-Harbor-Registry-using-REST-API
 
# Create project
# curl -u "admin:1qaz@WSX" -i -k -X POST -H "Content-Type: application/json" -d "{"project_name":"dev2"}" "https://reg.dev.mta4.ru/api/projects?project"
 
# List of all repositories
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories?project_id=1"
 
# List of all images include labels for repository
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories/dev/hello/tags"
 
# List of all policies
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/policies/replication"
 
# Job Status of replication (running or finishing)
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/jobs/replication?policy_id=13"
 
# Manual execution replication
# curl -u "admin:1qaz@WSX" -i -k -X POST -H "Content-type: application/json" -d "{"policy_id":13}" "https://reg.dev.mta4.ru/api/replications"
 
# Other
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/systeminfo"
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/projects"
# curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories/dev/hello/labels"
# ----------------------------------------------------------------------------------------------------
 
# Usage:
#        /home/lagutinra/Документы/harbor/harbor.api.repl.by.label.py -exec [inc|full]
 
 
import os
import ssl
import sys
import json
import time
# import psutil
import base64
 
from urllib.request import Request, urlopen
from urllib.error import URLError
 
 
HARBOR_URL_API = 'https://reg.dev.mta4.ru/api'
HARBOR_USERNAME = 'admin'
HARBOR_PASSWORD = '1qaz@WSX'
HARBOR_POLICY_DESC = 'repl'
HARBOR_POLICY_ATTEMPT_COUNT = 9
HARBOR_POLICY_ATTEMPT_COUNT_DELAY = 30
HARBOR_SCRIPTNAME = os.path.abspath(__file__)
HARBOR_SCRIPTNAME_PID = os.path.dirname(HARBOR_SCRIPTNAME) + '/' + os.path.basename(HARBOR_SCRIPTNAME) + '.pid'
HARBOR_SCRIPTNAME_JSON = os.path.dirname(HARBOR_SCRIPTNAME) + '/' + os.path.basename(HARBOR_SCRIPTNAME) + '.json'
 
HARBOR_REPL_RESULT = list() # return main()
 
INSECURE_CONTEXT = ssl._create_unverified_context()
 
 
class bcolors(object):
 
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
 
 
def harbor_api(url, data=None, username=None, password=None):
    '''
    # GET anonymous
    url='https://reg.dev.mta4.ru/api/systeminfo'
    res_get_data=harbor_api(url)
    print(json.dumps(res_get_data, indent=4))
  
    # GET auth
    username='admin'
    password='1qaz@WSX'
    url='https://reg.dev.mta4.ru/api/policies/replication'
    res_get_data=harbor_api(url, username=username, password=password)
    print(json.dumps(res_get_data, indent=4))
  
    # POST auth
    username='admin'
    password='1qaz@WSX'
    url='https://reg.dev.mta4.ru/api/projects?project'
    json_data={'project_name':'dev9'}
    res_get_data=harbor_api(url, data=json_data, username=username, password=password)
    '''
  
    if data:
        params = json.dumps(data).encode('utf8')
        req = Request(url, data=params, headers={'content-type': 'application/json'})
  
    else:
        req = Request(url)
  
    if username and password:
        credentials = ('%s:%s' % (username, password))
        encoded_credentials = base64.b64encode(credentials.encode('utf8'))
        req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("utf8"))
  
    try:
        with urlopen(req, context=INSECURE_CONTEXT) as response:
            res = response.read()
  
        if data:
            return True
  
        else:
            return json.loads(res.decode("utf-8"))
  
    except:
  
        return False


def harbor_count_repo(repo_name, label_col):

    harbor_count_repo_data = 0
    harbor_count_repo_res = dict()

    harbor_count_repo_items = harbor_api(HARBOR_URL_API + '/repositories/' + str(repo_name) + '/tags', username=HARBOR_USERNAME, password=HARBOR_PASSWORD)

    if harbor_count_repo_items:

        tag_col_check = list()

        for harbor_count_repo_item in harbor_count_repo_items:

            labels_items = harbor_count_repo_item['labels']
  
            if labels_items:

                label_col_check = list()
  
                for labels_item in labels_items:
  
                    label_col_check.append(labels_item['name'])
  
                label_col.sort()
                label_col_check.sort()

                # print(str(repo_name) + ':' + str(harbor_count_repo_item['name']))
                # print('label policy: ' + str(label_col))
                # print('label repo: ' + str(label_col_check))

                if label_col == label_col_check:

                    harbor_count_repo_data += 1
                    tag_col_check.append(harbor_count_repo_item['name'])

    else:

        return False

    tag_col_check.sort()
    harbor_count_repo_res = {
        'repo_count': harbor_count_repo_data,
        'repo_tags': tag_col_check
    }

    # return harbor_count_repo_data
    return harbor_count_repo_res


def harbor_col_repo(project_id, label_col):
  
    harbor_col_repo_data = list()
  
    harbor_col_repo_items = harbor_api(HARBOR_URL_API + '/repositories?project_id=' + str(project_id), username=HARBOR_USERNAME, password=HARBOR_PASSWORD)
      
    if harbor_col_repo_items:
  
        for harbor_col_repo_item in harbor_col_repo_items:
  
            repo_id = harbor_col_repo_item['id']
            repo_name = harbor_col_repo_item['name']
  
            if repo_id and repo_name:
  
                harbor_count_repo_res = harbor_count_repo(repo_name, label_col)

                if harbor_count_repo_res:

                    if harbor_count_repo_res['repo_count'] > 0:

                        harbor_col_repo_data.append({'repo_id': repo_id, 'repo_name': repo_name, 'repo_count': harbor_count_repo_res['repo_count'], 'repo_tags': harbor_count_repo_res['repo_tags']})
  
    else:

        return False

    return harbor_col_repo_data


def harbor_col():

    harbor_col_data = list()

    harbor_api_items = harbor_api(HARBOR_URL_API + '/policies/replication', username=HARBOR_USERNAME, password=HARBOR_PASSWORD)

    if not harbor_api_items:

        return False

    for harbor_api_item in harbor_api_items:

        # print(json.dumps(harbor_api_item, indent=4))
        policy_name = False; policy_id = False; policy_description = False; project_name = False; project_id = False

        if harbor_api_item.get('name', False) and harbor_api_item.get('id', False) and harbor_api_item.get('description', False) and harbor_api_item.get('projects', False) and harbor_api_item.get('filters', False):

            try:
                policy_name = harbor_api_item['name']
                policy_id = harbor_api_item['id']
                policy_description = harbor_api_item['description']
                project_name = harbor_api_item['projects'][0]['name']
                project_id = harbor_api_item['projects'][0]['project_id']

            except:
                pass

            label_col = list()

            for filter_item in harbor_api_item['filters']:

                if filter_item['kind'] == 'label':

                    try:
                        label_col.append(filter_item['value']['name'])

                    except:
                        pass

        # print(policy_name, policy_id, policy_description, project_name, project_id, label)
        if policy_name and policy_id and policy_description and project_name and project_id and label_col:
  
            if policy_description == HARBOR_POLICY_DESC:
  
                harbor_col_repo_res = harbor_col_repo(project_id, label_col)
                  
                if harbor_col_repo_res:
  
                    harbor_col_data.append({'policy_name': policy_name, 'policy_id': policy_id, 'policy_description': policy_description, 'project_name': project_name, 'project_id': project_id, 'label': label_col, 'repo': harbor_col_repo_res})

    return harbor_col_data


def harbor_col_save(harbor_col_file, harbor_col_data):

    try:
        with open(harbor_col_file, 'wt', encoding='utf-8') as f:
            f.write(json.dumps(harbor_col_data, indent=4))

        # os.chmod(harbor_col_file, 0o777)

    except:
        return False

    if os.path.exists(harbor_col_file) and os.path.isfile(harbor_col_file):

        return True

    else:
        return False


def harbor_col_open(harbor_col_file):

    if os.path.exists(harbor_col_file) and os.path.isfile(harbor_col_file):

        try:
            with open(harbor_col_file, 'rt', encoding='utf-8') as f:
                return json.load(f)

        except:
            return False

    else:
        return False


def harbor_col_delete(harbor_col_file):

    if os.path.exists(harbor_col_file) and os.path.isfile(harbor_col_file):

        try:
            os.remove(harbor_col_file)

        except:

            return False

    return True


def harbor_col_pars(harbor_col_res_new, harbor_col_res_old=None):

    harbor_col_pars_data = list()

    for harbor_col_res_new_item in harbor_col_res_new:

        policy_id = harbor_col_res_new_item['policy_id']
        policy_name = harbor_col_res_new_item['policy_name']

        policy_flag = False

        if harbor_col_res_old:

            for harbor_col_res_old_item in harbor_col_res_old:

                policy_id_old = harbor_col_res_old_item['policy_id']
                policy_name_old = harbor_col_res_old_item['policy_name']

                if policy_id == policy_id_old and policy_name == policy_name_old:

                    policy_flag = True

                    if harbor_col_res_new_item['repo'] == harbor_col_res_old_item['repo']:

                        # print(str(policy_name) + ': identical')
                        harbor_col_pars_data.append({'policy_name': str(policy_name), 'policy_id': policy_id, 'policy_status': 'identical'})

                    else:

                        # print(str(policy_name) + ': not identical')
                        harbor_col_pars_data.append({'policy_name': str(policy_name), 'policy_id': policy_id, 'policy_status': 'not identical'})

        if not policy_flag:

            # print(str(policy_name) + ': not found')
            harbor_col_pars_data.append({'policy_name': str(policy_name), 'policy_id': policy_id, 'policy_status': 'not found'})

    if harbor_col_pars_data:

        return harbor_col_pars_data

    else:
         return False


def harbor_repl_check(policy_id):
  
    harbor_repl_check_res = harbor_api(HARBOR_URL_API + '/jobs/replication?policy_id=' + str(policy_id), username=HARBOR_USERNAME, password=HARBOR_PASSWORD)
  
    if not harbor_repl_check_res:
  
        return False
  
    for harbor_repl_check_res_item in harbor_repl_check_res:
  
        if harbor_repl_check_res_item['status'] == 'running':
  
            return False
  
    return True
  
  
def harbor_repl_exec(policy_id):
  
    harbor_repl_exec_res = harbor_api(HARBOR_URL_API + '/replications', data={'policy_id': policy_id}, username=HARBOR_USERNAME, password=HARBOR_PASSWORD)
  
    if harbor_repl_exec_res:
  
        return True
  
    else:
  
        return False
  
  
def harbor_repl(harbor_col_pars_res, verbose=False):
 
    err_count = 0
 
    if verbose:
        print('----------------------------------------------------------------------------------------------------')
        print(bcolors.BOLD + 'Replication progress:' + bcolors.ENDC)
 
    for harbor_col_pars_res_item in harbor_col_pars_res:
  
        count = 0
  
        if harbor_col_pars_res_item['policy_status'] != 'identical':
  
            while count <= HARBOR_POLICY_ATTEMPT_COUNT:
  
                harbor_col_pars_res_item['repl_attempt'] = count
                # print('exec attempt(' + bcolors.BOLD + str(count) + bcolors.ENDC + '): ' + bcolors.HEADER + str(harbor_col_pars_res_item) + bcolors.ENDC, end=' ')
  
                if harbor_repl_check(harbor_col_pars_res_item['policy_id']):
  
                    if harbor_repl_exec(harbor_col_pars_res_item['policy_id']):
  
                        harbor_col_pars_res_item['repl_status'] = 'True'
                        # print(bcolors.OKGREEN + '- True' + bcolors.ENDC, flush=True)
                        if verbose: print(bcolors.OKGREEN + str(harbor_col_pars_res_item) + bcolors.ENDC)
                         
                        break
 
                    else:
  
                        harbor_col_pars_res_item['repl_status'] = 'Warning'
                        # print(bcolors.WARNING + '- Warning' + bcolors.ENDC, flush=True)
                        if verbose: print(bcolors.WARNING + str(harbor_col_pars_res_item) + bcolors.ENDC)
  
                else:
  
                    harbor_col_pars_res_item['repl_status'] = 'Warning'
                    # print(bcolors.WARNING + '- Warning' + bcolors.ENDC, flush=True)
                    if verbose: print(bcolors.WARNING + str(harbor_col_pars_res_item) + bcolors.ENDC)
  
                time.sleep(HARBOR_POLICY_ATTEMPT_COUNT_DELAY)
                count += 1
              
            else:
  
                harbor_col_pars_res_item['repl_attempt'] = count
                harbor_col_pars_res_item['repl_status'] = 'False'
                # print('exec attempt(' + bcolors.BOLD + str(count) + bcolors.ENDC + '): ' + bcolors.HEADER + str(harbor_col_pars_res_item) + bcolors.ENDC, end=' ')
                # print(bcolors.FAIL + '- False' + bcolors.ENDC, flush=True)
                if verbose: print(bcolors.FAIL + str(harbor_col_pars_res_item) + bcolors.ENDC)
                 
                err_count += 1
 
        else:
  
            harbor_col_pars_res_item['repl_attempt'] = count
            harbor_col_pars_res_item['repl_status'] = 'Null'
            # print('exec attempt(' + bcolors.BOLD + str(count) + bcolors.ENDC + '): ' + bcolors.HEADER + str(harbor_col_pars_res_item) + bcolors.ENDC, end=' ')
            # print(bcolors.OKGREEN + '- Null' + bcolors.ENDC, flush=True)       
            if verbose: print(bcolors.OKGREEN + str(harbor_col_pars_res_item) + bcolors.ENDC)
 
        HARBOR_REPL_RESULT.append(harbor_col_pars_res_item)
 
    if verbose: print('----------------------------------------------------------------------------------------------------')
 
    if err_count == 0:
 
        return True
 
    else:
        return False
 
 
def harbor_conf(verbose=False):
 
    harbor_col_res_new = harbor_col()
 
    if not harbor_col_res_new:
 
        return False
 
    else:
 
        harbor_col_res_old = harbor_col_open(HARBOR_SCRIPTNAME_JSON)
        harbor_col_pars_res = harbor_col_pars(harbor_col_res_new, harbor_col_res_old)
 
        if harbor_col_pars_res:
 
            if  harbor_repl(harbor_col_pars_res):
            # if harbor_repl(harbor_col_pars_res, verbose=True):
 
                harbor_repl_status = True
             
            else:
 
                harbor_repl_status = False
 
        else:
 
            return False
 
    if harbor_repl_status:
 
        if verbose:
            print(bcolors.BOLD + 'Current settings in ' + HARBOR_SCRIPTNAME_JSON + ':' + bcolors.ENDC + '\n' + bcolors.WARNING + json.dumps(harbor_col_res_new, indent=4) + bcolors.ENDC)
            print('----------------------------------------------------------------------------------------------------')
 
        return harbor_col_res_new
 
    else:
        return False
 
 
def usage():
  
    print('----------------------------------------------------------------------------------------------------')
    print(bcolors.OKGREEN + 'NAME:   HARBOR.API.REPL.BY.LABEL.PY' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'DESC:   CHECK NEW IMAGES IN REPO WITH ASSIGNED LABEL(S) AND START REPLICATION IF REQURED' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'DATE:   31-12-2018' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'LANG:   PYTHON 3' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'AUTHOR: LAGUTIN R.A.' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'EMAIL:  RLAGUTIN@MTA4.RU' + bcolors.ENDC)
    print('----------------------------------------------------------------------------------------------------')
    print(bcolors.BOLD + 'Harbor Rest API' + bcolors.ENDC)
    print()
    print(bcolors.OKBLUE + 'http://editor.swagger.io/' + bcolors.ENDC)
    print(bcolors.OKBLUE + 'https://raw.githubusercontent.com/goharbor/harbor/master/docs/swagger.yaml' + bcolors.ENDC)
    print(bcolors.OKBLUE + 'https://community.pivotal.io/s/article/How-to-Browse-and-Query-Harbor-Registry-using-REST-API' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'Create project' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X POST -H "Content-Type: application/json" -d "{"project_name":"dev2"}" "https://reg.dev.mta4.ru/api/projects?project"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'List of all repositories' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories?project_id=1"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'List of all images include labels for repository' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories/dev/hello/tags"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'List of all policies' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/policies/replication"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'Job Status of replication (running or finishing)' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/jobs/replication?policy_id=13"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'Manual execution replication' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X POST -H "Content-type: application/json" -d "{"policy_id":13}" "https://reg.dev.mta4.ru/api/replications"' + bcolors.ENDC)
    print()
    print(bcolors.BOLD + 'Other' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/systeminfo"' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/projects"' + bcolors.ENDC)
    print(bcolors.WARNING + 'curl -u "admin:1qaz@WSX" -i -k -X GET -H "Content-type: application/json" "https://reg.dev.mta4.ru/api/repositories/dev/hello/labels"' + bcolors.ENDC)
    print('----------------------------------------------------------------------------------------------------')
    print()
    print(bcolors.BOLD + 'Usage: ' + bcolors.ENDC)
    print(bcolors.FAIL + '       ' + HARBOR_SCRIPTNAME + ' -exec [inc|full]' + bcolors.ENDC)
    print()
 
    sys.exit(0)
 
 
def pid_file(pidpath, mode):
 
    if mode == 'create':
 
        pid = str(os.getpid())
 
        try:
            with open(pidpath, 'wt') as f:
                f.write(pid)
 
        except:
            print("%s fail created" % pidpath)
            sys.exit(1)  
 
    elif mode == 'check':
 
        if os.path.isfile(pidpath):
 
            print("%s already exists, exiting" % pidpath)
            sys.exit(1)
 
    elif mode == 'remove':
 
        try:
            os.remove(pidpath)
 
        except:
            print("%s fail removed" % pidpath)
            sys.exit(1)
 
 
def main():
  
    if len(sys.argv) != 3:
  
        usage()
  
    if sys.argv[1] != '-exec':
  
        usage()
  
    if sys.argv[2] == 'inc':
  
        pid_file(HARBOR_SCRIPTNAME_PID, 'check')
        pid_file(HARBOR_SCRIPTNAME_PID, 'create')
  
        harbor_conf_res = harbor_conf()
        # harbor_conf_res = harbor_conf(verbose=True)
 
        if harbor_conf_res:
 
            if not harbor_col_save(HARBOR_SCRIPTNAME_JSON, harbor_conf_res):
             
                print("%s fail saved" % HARBOR_SCRIPTNAME_JSON)
                pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
                sys.exit(1)
 
        else:
 
            print('failed parsing harbor settings')
            pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
            sys.exit(1)
 
        pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
 
        # print(HARBOR_REPL_RESULT)
        # print(bcolors.BOLD + 'Result: ' + bcolors.ENDC)
        return json.dumps(HARBOR_REPL_RESULT, indent=4)
 
    elif sys.argv[2] == 'full':
  
        pid_file(HARBOR_SCRIPTNAME_PID, 'check')
        pid_file(HARBOR_SCRIPTNAME_PID, 'create')
   
        if not harbor_col_delete(HARBOR_SCRIPTNAME_JSON):
 
            print("%s fail removed" % HARBOR_SCRIPTNAME_JSON)
            pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
            sys.exit(1)
 
        harbor_conf_res = harbor_conf()
        # harbor_conf_res = harbor_conf(verbose=True)
 
        if harbor_conf_res:
 
            if not harbor_col_save(HARBOR_SCRIPTNAME_JSON, harbor_conf_res):
             
                print("%s fail saved" % HARBOR_SCRIPTNAME_JSON)
                pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
                sys.exit(1)
 
        else:
 
            print('failed parsing harbor settings')
            pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
            sys.exit(1)
 
        pid_file(HARBOR_SCRIPTNAME_PID, 'remove')
 
        # print(HARBOR_REPL_RESULT)
        # print(bcolors.BOLD + 'Result: ' + bcolors.ENDC)
        return json.dumps(HARBOR_REPL_RESULT, indent=4)
 
    else:
        usage()
 
 
if __name__ == '__main__':
 
    sys.exit(main())
