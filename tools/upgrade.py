#!/usr/bin/python3

import os, json, sys

fspath="/opt/docklet"

def update_quotainfo():
    if not os.path.exists(fspath+"/global/sys/quotainfo"):
        print("quotainfo file not exists, please run docklet to init it")
        return False
    quotafile = open(fspath+"/global/sys/quotainfo", 'r')
    quotas = json.loads(quotafile.read())
    quotafile.close()
    if type(quotas) is list:
        new_quotas = {}
        new_quotas['default'] = 'fundation'
        new_quotas['quotainfo'] = quotas
        quotas = new_quotas
        print("change the type of quotafile from list to dict")
    keys = []
    for quota in quotas['quotainfo']:
        keys.append(quota['name'])
    if 'cpu' not in keys:
        quotas['quotainfo'].append({'name':'cpu', 'hint':'the cpu quota, number of cores, e.g. 4'})
    if 'memory' not in keys:
        quotas['quotainfo'].append({'name':'memory', 'hint':'the memory quota, number of MB, e.g. 4000'})
    if 'disk' not in keys:
        quotas['quotainfo'].append({'name':'disk', 'hint':'the disk quota, number of MB, e.g. 4000'})
    if 'data' not in keys:
        quotas['quotainfo'].append({'name':'data', 'hint':'the quota of data space, number of GB, e.g. 100'})
    if 'image' not in keys:
        quotas['quotainfo'].append({'name':'image', 'hint':'how many images the user can have, e.g. 8'})
    if 'idletime' not in keys:
        quotas['quotainfo'].append({'name':'idletime', 'hint':'will stop cluster after idletime, number of hours, e.g. 24'})
    if 'vnode' not in keys:
        quotas['quotainfo'].append({'name':'vnode', 'hint':'how many containers the user can have, e.g. 8'})
    print("quotainfo updated")
    quotafile = open(fspath+"/global/sys/quotainfo", 'w')
    quotafile.write(json.dumps(quotas))
    quotafile.close()

def allquota():
    try:
        quotafile = open(fspath+"/global/sys/quota", 'r')
        quotas = json.loads(quotafile.read())
        quotafile.close()
        return quotas
    except Exception as e:
        print(e)
        return None

def quotaquery(quotaname,quotas):
    for quota in quotas:
        if quota['name'] == quotaname:
            return quota['quotas']
    return None

def enable_gluster_quota():
    conffile=open("../conf/docklet.conf",'r')
    conf=conffile.readlines()
    conffile.close()
    enable = False
    volume_name = ""
    for line in conf:
        if line.startswith("DATA_QUOTA"):
            keyvalue = line.split("=")
            if len(keyvalue) < 2:
                continue
            key = keyvalue[0].strip()
            value = keyvalue[1].strip()
            if value == "YES":
                enable = True
                break
    for line in conf:
        if line.startswith("DATA_QUOTA_CMD"):
            keyvalue = line.split("=")
            if len(keyvalue) < 2:
                continue
            volume_name = keyvalue[1].strip()
    if not enable:
        print("don't need to enable the quota")
        return
    
    users = User.query.all()
    quotas = allquota()
    if quotaquery == None:
        print("quota info not found")
        return
    sys_run("gluster volume quota %s enable" % volume_name)
    for user in users:
        quota = quotaquery(user.user_group, quotas)
        nfs_quota = quota['data']
        if nfs_quota == None:
            print("data quota should be set")
            return
        nfspath = "/users/%s/data" % user.username
        sys_run("gluster volume quota %s limit-usage %s %sGB" % (volume_name,nfspath,nfs_quota))

if __name__ == '__main__':
    update_quotainfo()
#    enable_gluster_quota()
