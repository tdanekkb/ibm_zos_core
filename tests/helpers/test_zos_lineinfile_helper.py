# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
import os
from shellescape import quote
from pprint import pprint

__metaclass__ = type


def set_uss_test_env(test_name, hosts, test_env):
    test_env["TEST_FILE"] = test_env["TEST_DIR"] + test_name
    try:
        if not os.path.exists(test_env["TEST_DIR"]):
            os.mkdir(test_env["TEST_DIR"])
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], test_env["TEST_FILE"]))
    except:
        assert 1==0, "Failed to set the test env"

def clean_uss_test_env(test_dir, hosts):
    try:
        hosts.all.shell(cmd="rm -rf " + test_dir)
    except:
        assert 1==0, "Failed to clean the test env"

def test_uss_general(test_name, ansible_zos_module, test_env, test_info):
    hosts = ansible_zos_module
    set_uss_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["TEST_FILE"]
    results = hosts.all.zos_lineinfile(**test_info)
    clean_uss_test_env(test_env["TEST_DIR"], hosts)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") == 1

def set_ds_test_env(test_name, hosts, test_env):
    TEMP_FILE = "/tmp/" + test_name
    encoding = test_env["ENCODING"].replace("-", "").replace(".", "").upper()
    
    try:
        int(encoding[0])
        encoding = "E" + encoding
    except:
        pass
    if len(encoding) > 7:
        encoding = encoding[:4] + encoding[-4:]

    test_env["DS_NAME"] = test_name.upper() + "." + encoding + "." + test_env["DS_TYPE"]
    cmdStr = "python -c \"from zoautil_py import Datasets; Datasets.create('" + test_env["DS_NAME"] + "', type='" + test_env["DS_TYPE"] + "')\" "

    try:
        hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], TEMP_FILE))
        if test_env["DS_TYPE"] in ["PDS", "PDSE"]:
            test_env["DS_NAME"] =  test_env["DS_NAME"] + "(MEM)"
            hosts.all.zos_data_set(name=test_env["DS_NAME"], state="present", type="member")
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), test_env["DS_NAME"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), test_env["DS_NAME"])

        if test_env["ENCODING"] != "IBM-1047":
            hosts.all.zos_encode(src=TEMP_FILE, dest=test_env["DS_NAME"], from_encoding="IBM-1047", to_encoding=test_env["ENCODING"])
        else:
            hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
        cmdStr = "cat \"//'{0}'\" | wc -l ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        pprint(vars(results))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
    except:
        assert 1==0, "Failed to set the test env"

def clean_ds_test_env(ds_name, hosts):
    ds_name = ds_name.replace("(MEM)", "")
    cmdStr = "python -c \"from zoautil_py import Datasets; Datasets.delete('" + ds_name + "')\" "
    try:
        hosts.all.shell(cmd=cmdStr)
    except:
        assert 1==0, "Failed to clean the test env"

def test_ds_general(test_name, ansible_zos_module, test_env, test_info):
    hosts = ansible_zos_module
    set_ds_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["DS_NAME"]
    if test_env["ENCODING"]:
        test_info["encoding"] = test_env["ENCODING"]
    results = hosts.all.zos_lineinfile(**test_info)
    clean_ds_test_env(test_env["DS_NAME"], hosts)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") == 1