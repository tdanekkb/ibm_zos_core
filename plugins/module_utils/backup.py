# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
from ansible.module_utils.six import PY3
from ansible.module_utils.basic import AnsibleModule
import time
from shutil import copy2, copytree, rmtree
from stat import S_IREAD, S_IWRITE, ST_MODE
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.file import make_dirs

try:
    from zoautil_py import Datasets
except Exception:
    Datasets = MissingZOAUImport()
if PY3:
    from shlex import quote
else:
    from pipes import quote


def _validate_data_set_name(ds):
    arg_defs = dict(ds=dict(arg_type="data_set"))
    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args({"ds": ds})
    return parsed_args.get("ds")


def mvs_file_backup(dsn, bk_dsn):
    """Create a backup data set for an MVS data set

    Arguments:
        dsn {str} -- The name of the data set to backup.
                        It could be an MVS PS/PDS/PDSE/VSAM(KSDS), etc.
        bk_dsn {str} -- The name of the backup data set.

    Raises:
        BackupError: When backup data set exists.
        BackupError: When creation of backup data set fails.
    """
    if not bk_dsn:
        hlq = Datasets.hlq()
        bk_dsn = Datasets.temp_name(hlq)
    dsn = _validate_data_set_name(dsn).upper()
    bk_dsn = _validate_data_set_name(bk_dsn).upper()

    cp_rc = _copy_ds(dsn, bk_dsn)
    # The data set is probably a PDS or PDSE
    if cp_rc == 12:
        # Delete allocated backup that was created when attempting to use _copy_ds()
        # Safe to delete because _copy_ds() would have raised an exception if it did
        # not successfully create the backup data set, so no risk of it predating module invocation
        Datasets.delete(bk_dsn)
        if Datasets.move(dsn, bk_dsn) == 0:
            _allocate_model(dsn, bk_dsn)
        else:
            raise BackupError(
                "Unable to backup data set {0} to {1}".format(dsn, bk_dsn)
            )
    return bk_dsn


def uss_file_backup(path, backup_name=None, compress=False):
    """Create a backup file for a USS file or path

    Arguments:
        path {str} -- The name of the USS file or path to backup.
        backup_name {str} -- The name of the backup file.

    Keyword Arguments:
        compress {bool} -- Determines if the backup be compressed. (default: {False})

    Raises:
        BackupError: When creating compressed backup fails.

    Returns:
        str -- Name of the backup file.
    """
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        raise BackupError("Path to be backed up does not exist.")

    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)

    ext = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()).lower()
    if os.path.isdir(abs_path):
        default_backup_name = "{0}@{1}-bak".format(abs_path[:-1], ext)
    else:
        default_backup_name = "{0}@{1}-bak".format(abs_path, ext)

    backup_base = os.path.basename(default_backup_name)
    backup_name_provided = True

    if not backup_name:
        backup_name = default_backup_name
        backup_name_provided = False

    if os.path.isdir(abs_path) and backup_name[-1] != "/" and not compress:
        backup_name += "/"
        make_dirs(backup_name, mode_from=abs_path)
    if backup_name[-1] == "/" and not os.path.isdir(backup_name):
        make_dirs(backup_name)
    elif os.path.isdir(backup_name) and backup_name[-1] != "/":
        backup_name += "/"

    if compress:
        if backup_name_provided and os.path.isdir(backup_name):
            backup_name += backup_base
        bk_cmd = "tar -cpf {0}.tar {1}".format(quote(backup_name), quote(abs_path))
        rc, out, err = module.run_command(bk_cmd)
        if rc:
            raise BackupError(err)
        backup_name += ".tar"
    else:
        if os.path.isdir(abs_path):
            if os.path.exists(backup_name):
                rmtree(backup_name)
            copytree(abs_path, backup_name)
        elif not os.path.isdir(abs_path) and os.path.isdir(backup_name):
            backup_name = backup_name + os.path.basename(abs_path)
            copy2(abs_path, backup_name)
        else:
            copy2(abs_path, backup_name)

    return backup_name


def _copy_ds(ds, bk_ds):
    """Copy the contents of a data set to another

    Arguments:
        ds {str} -- The source data set to be copied from. Should be SEQ or VSAM
        bk_dsn {str} -- The destination data set to copy to.

    Raises:
        BackupError: When copying data fails
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    _allocate_model(bk_ds, ds)
    repro_cmd = """  REPRO -
    INDATASET({0}) -
    OUTDATASET({1})""".format(
        ds, bk_ds
    )
    rc, out, err = module.run_command(
        "mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin", data=repro_cmd
    )
    if rc != 0 and rc != 12:
        Datasets.delete(bk_ds)
        raise BackupError(
            "Unable to backup data set {0}; stdout: {1}; stderr: {2}".format(
                ds, out, err
            )
        )
    if rc != 0 and _vsam_empty(ds):
        rc = 0
    return rc


def _allocate_model(ds, model):
    """Allocate a data set using allocation information of a model data set

    Arguments:
        ds {str} -- The name of the data set to be allocated.
        model {str} -- The name of the data set whose allocation parameters should be used.

    Raises:
        BackupError: When allocation fails
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    alloc_cmd = """  ALLOC -
    DS('{0}') -
    LIKE('{1}')""".format(ds, model)
    cmd = "mvscmdauth --pgm=ikjeft01 --systsprt=* --systsin=stdin"
    rc, out, err = module.run_command(cmd, data=alloc_cmd)
    if rc != 0:
        raise BackupError(
            "Unable to allocate data set {0}; stdout: {1}; stderr: {2}".format(
                ds, out, err
            )
        )
    return rc


def _vsam_empty(ds):
    """Determine if a VSAM data set is empty.

    Arguments:
        ds {str} -- The name of the VSAM data set.

    Returns:
        bool - If VSAM data set is empty.
        Returns True if VSAM data set exists and is empty.
        False otherwise.
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    empty_cmd = """  PRINT -
    INFILE(MYDSET) -
    COUNT(1)"""
    rc, out, err = module.run_command(
        "mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin --mydset={0}".format(ds),
        data=empty_cmd,
    )
    if rc == 4 or "VSAM OPEN RETURN CODE IS 160" in out:
        return True
    elif rc != 0:
        return False


class BackupError(Exception):
    def __init__(self, message):
        self.msg = 'An error occurred during backup: "{0}"'.format(message)
        super(BackupError, self).__init__(self.msg)
