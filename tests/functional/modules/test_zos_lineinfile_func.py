# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helpers'))
from test_zos_lineinfile_helper import test_uss_general, test_ds_general

__metaclass__ = type

TEST_CONTENT = """
if [ -z "$STEPLIB" ] && tty -s;
then
    export STEPLIB=none
    exec -a $0 $SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin    
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/$LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
"""

DS_TYPE = ['SEQ', 'PDS', 'PDSE']
ENCODING = ['IBM-1047', 'ISO8859-1']

TEST_ENV = dict(
    TEST_CONT = TEST_CONTENT,
    TEST_DIR = "/tmp/zos_lineinfile/",
    TEST_FILE = "",
    DS_NAME = "",
    DS_TYPE = "",
    ENCODING = "",
)

TEST_INFO = dict(
    test_uss_line_replace = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_insertafter_regex = dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_insertbefore_regex = dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present"),
    test_uss_line_insertafter_eof = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present"),
    test_uss_line_insertbefore_bof = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present"),
    test_uss_line_replace_match_insertafter_ignore = dict(regexp="ZOAU_ROOT=", insertafter="PATH=", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_match_insertbefore_ignore = dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_replace_nomatch_insertafter_match = dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_nomatch_insertbefore_match = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_replace_nomatch_insertafter_nomatch = dict(regexp="abcxyz", insertafter="xyzijk", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_nomatch_insertbefore_nomatch = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_absent = dict(regexp="ZOAU_ROOT=", state="absent"),
    test_ds_line_replace = dict(test_name="T1"),
    test_ds_line_insertafter_regex = dict(test_name="T2"),
    test_ds_line_insertbefore_regex = dict(test_name="T3"),
    test_ds_line_insertafter_eof = dict(test_name="T4"),
    test_ds_line_insertbefore_bof = dict(test_name="T5"),
    test_ds_line_replace_match_insertafter_ignore = dict(test_name="T6"),
    test_ds_line_replace_match_insertbefore_ignore = dict(test_name="T7"),
    test_ds_line_replace_nomatch_insertafter_match = dict(test_name="T8"),
    test_ds_line_replace_nomatch_insertbefore_match = dict(test_name="T9"),
    test_ds_line_replace_nomatch_insertafter_nomatch = dict(test_name="T10"),
    test_ds_line_replace_nomatch_insertbefore_nomatch = dict(test_name="T11"),
    test_ds_line_absent = dict(test_name="T12"),
)

#########################
# USS test cases
#########################

@pytest.mark.uss
def test_uss_line_replace(ansible_zos_module):
    test_uss_general("test_uss_line_replace", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace"])

@pytest.mark.uss
def test_uss_line_insertafter_regex(ansible_zos_module):
    test_uss_general("test_uss_line_insertafter_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_regex"])

@pytest.mark.uss
def test_uss_line_insertbefore_regex(ansible_zos_module):
    test_uss_general("test_uss_line_insertbefore_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_regex"])

@pytest.mark.uss
def test_uss_line_insertafter_eof(ansible_zos_module):
    test_uss_general("test_uss_line_insertafter_eof", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_eof"])

@pytest.mark.uss
def test_uss_line_insertbefore_bof(ansible_zos_module):
    test_uss_general("test_uss_line_insertbefore_bof", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_bof"])

@pytest.mark.uss
def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    test_uss_general("test_uss_line_replace_match_insertafter_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertafter_ignore"])

@pytest.mark.uss
def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    test_uss_general("test_uss_line_replace_match_insertbefore_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertbefore_ignore"])

@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertafter_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_match"])

@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertbefore_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_match"])

@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertafter_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_nomatch"])

@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertbefore_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_nomatch"])

@pytest.mark.uss
def test_uss_line_absent(ansible_zos_module):
    test_uss_general("test_uss_line_absent", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_absent"])

#########################
# Dataset test cases
#########################

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_insertafter_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_insertafter_regex"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_regex"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_insertbefore_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_insertbefore_regex"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_regex"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_insertafter_eof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_insertafter_eof"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_eof"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_insertbefore_bof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_insertbefore_bof"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_bof"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_match_insertafter_ignore"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertafter_ignore"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_match_insertbefore_ignore"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertbefore_ignore"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_nomatch_insertafter_match"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_match"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_nomatch_insertbefore_match"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_match"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_nomatch_insertafter_nomatch"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_nomatch"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_replace_nomatch_insertbefore_nomatch"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_nomatch"])

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_line_absent(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    test_ds_general(TEST_INFO["test_ds_line_absent"]["test_name"], ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_absent"])
