#!/usr/bin/python
# -*- coding: utf-8 -*-​
# Copyright (c) IBM Corporation 2019, 2020
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: zos_copy
version_added: '0.0.3'
short_description: Copy data to z/OS
description:
    - The M(zos_copy) module copies a file or data set from a local or a
      remote machine to a location on the remote machine.
    - Use the M(zos_fetch) module to copy files or data sets from remote 
      locations to local machine.
author: "Asif Mahmud (@asifmahmud)"
options:
  src:
    description:
    - Absolute local path to a file to copy to the remote z/OS system.
    - If I(remote_src=true), then src must be the path to a file, name of a 
      data set or data set member on remote z/OS system.
    - If the path is a directory, destination must be a partitioned
      data set.
    - If the path is a file and dest ends with "/", the file is copied to the
      folder with the same filename.
    - Required unless using C(content).
    type: str
  dest:
    description:
    - Remote absolute path or data set where the file should be copied to.
    - Destination can be a USS location separated with ‘/’
      or MVS location separated with ‘.’.
    - If C(src) is a directory, this must be a partitioned data set.
    - If C(dest) is a nonexistent path, it will be created.
    - If C(dest) is a nonexistent data set, it will be allocated.
    - If C(src) and C(dest) are files and if the parent directory of C(dest)
      doesn't exist, then the task will fail.
    type: str
    required: yes
  content:
    description:
    - When used instead of C(src), sets the contents of a file or data set
      directly to the specified value.
    - Works only when C(dest) is a USS file, sequential data set or a
      partitioned data set member.
    - This is for simple values, for anything complex or with formatting please
      switch to the M(template) module.
    type: str
    required: false
  backup:
    description:
    - Sepcifies whether a backup should be created.
    - When set to C(true), the module creates a backup file including the 
      timestamp information.
    - For USS files the backup is located in the same directory as C(dest) with
      the format C(/path/to/dest/dir/filename.yyyy-mm-dd@hh:mm~).
    - Data sets will be backed up in a temporary data set, which will be
      returned as part of the C(backup_file) return parameter.
    type: bool
    default: false
    required: false
  force:
    description:
    - If C(true), the remote file or data set will be replaced when contents 
      are different than the source.
    - If C(false), the file will only be transferred if the destination does 
      not exist.
    type: bool
    default: true
    required: false
  mode:
    description:
    - The permission of the destination file or directory.
    - If C(dest) is USS, this will act as Unix file mode, otherwise ignored.
    - Refer to the M(copy) module for a detailed description of this parameter.
    type: str
    required: false
  remote_src:
    description:
    - If C(false), it will search for src at local machine.
    - If C(true), it will go to the remote/target machine for the src.
    type: bool
    default: false
    required: false
  local_follow:
    description:
    - This flag indicates that filesystem links in the source tree, if they 
      exist, should be followed.
    type: bool
    default: true
    required: false
  is_binary:
    description:
    - If C(true), indicates that the file or data set to be copied is a 
      binary file/data set. 
    type: bool
    default: false
    required: false
  is_vsam:
    description:
    - Indicates whether the destination data set is VSAM. 
    type: bool
    default: false
    required: false
  use_qualifier:
    description:
    - Add user qualifier to data sets.
    type: bool
    default: true
    required: false
  encoding:
    description:
    - Specifies which encodings the destination file or data set should be
      converted from and to. 
    - If this parameter is not provided, no encoding conversions will take 
      place.
    - Only valid if I(is_binary=false)
    type: dict
    required: false
    suboptions:
      from:
        description:
            - The encoding to be converted from
        required: true
        type: str
      to:
        description:
            - The encoding to be converted to
        required: true
        type: str
  checksum:
    description:
    - SHA256 checksum of the file being copied.
    - Used to validate that the copy of the file or data set was successful.
    type: str
    required: false
notes:
    - Destination data sets are assumed to be in catalog. When trying to copy 
      to an uncataloged data set, the module assumes that the data set does 
      not exist and will create it.
seealso:
- copy
- fetch
- zos_fetch
- zos_data_set
'''

EXAMPLES = r'''
- name: Copy a local file to a sequential data set
  zos_copy:
    src: /path/to/sample_seq_data_set
    dest: SAMPLE.SEQ.DATA.SET

- name: Copy a local file to a USS location
  zos_copy:
    src: /path/to/test.log
    dest: /tmp/test.log

- name: Copy a local ASCII encoded file and convert to IBM-1047
  zos_copy:
    src: /path/to/file.txt
    dest: /tmp/file.txt
    encoding:
      from: ISO8859-1
      to: IBM-1047

- name: Copy file with owner and permission details
  zos_copy:
    src: /path/to/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: '0644'

- name: Module will follow the symbolic link specified in src
  zos_copy:
    src: /path/to/link
    dest: /path/to/uss/location
    local_follow: true

- name: Copy a local file to a PDS member
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.PDSE(member_name)

- name: Copy a single file to a VSAM(KSDS)
  zos_copy:
    src: /path/to/local/file
    dest: SAMPLE.VSAM.DATA.SET
    is_vsam: true

- name: Copy inline content to a sequential dataset and replace existing data
  zos_copy:
    content: 'Inline content to be copied'
    dest: SAMPLE.SEQ.DATA.SET
    force: true

- name: Copy a USS file to a sequential data set
  zos_copy:
    src: /path/to/remote/uss/file
    dest: SAMPLE.SEQ.DATA.SET
    remote_src: true

- name: Copy a binary file to a PDSE member
  zos_copy:
    src: /path/to/binary/file
    dest: HLQ.SAMPLE.PDSE(member_name)
    is_binary: true

- name: Copy a local file and take a backup of the existing file
  zos_copy:
    src: /path/to/local/file
    dest: /path/to/dest
    backup: true

- name: Copy a PDS(E) on remote system to a new PDS(E)
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.NEW.PDSE
    remote_src: true

- name: Copy a PDS(E) on remote system to a PDS(E), replacing the original
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.EXISTING.PDSE
    remote_src: true
    force: true

- name: Copy PDS(E) member to a new PDS(E) member. Replace if it already exists
  zos_copy:
    src: HLQ.SAMPLE.PDSE(member_name)
    dest: HLQ.NEW.PDSE(member_name)
    force: true
    remote_src: true
'''

RETURN = r'''
dest:
    description: Destination file/path or MVS data set name.
    returned: success
    type: str
    sample: SAMPLE.SEQ.DATA.SET
file:
    description: Source file used for the copy on the target machine.
    returned: changed
    type: str
    sample: /path/to/source.log
checksum:
    description: SHA256 checksum of the file after running copy.
    returned: success and dest is USS
    type: str
    sample: 8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e
backup_file:
    description: Name of the backup file or data set that was created.
    returned: changed and if backup=true
    type: str
    sample: /path/to/file.txt.2015-02-03@04:15~
gid:
    description: Group id of the file, after execution
    returned: success and if dest is USS
    type: int
    sample: 100
group:
    description: Group of the file, after execution
    returned: success and if dest is USS
    type: str
    sample: httpd
owner:
    description: Owner of the file, after execution
    returned: success and if dest is USS
    type: str
    sample: httpd
uid:
    description: Owner id of the file, after execution
    returned: success and if dest is USS
    type: int
    sample: 100
mode:
    description: Permissions of the target, after execution
    returned: success and if dest is USS
    type: str
    sample: 0644
size:
    description: Size(in bytes) of the target, after execution.
    returned: success and dest is USS
    type: int
    sample: 1220
state:
    description: State of the target, after execution
    returned: success and if dest is USS
    type: str
    sample: file
msg:
    description: Failure message returned by the module
    returned: failure
    type: str
    sample: Error while gathering data set information
stdout:
    description: The stdout from a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: Copying local file /tmp/foo/src to remote path /tmp/foo/dest
stderr:
    description: The stderr of a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: FileNotFoundError: No such file or directory '/tmp/foo'
stdout_lines:
    description: List of strings containing individual lines from stdout
    returned: failure
    type: list
    sample: [u"Copying local file /tmp/foo/src to remote path /tmp/foo/dest.."]
stderr_lines:
    description: List of strings containing individual lines from stderr
    returned: failure
    type: list
    sample: [u"FileNotFoundError: No such file or directory '/tmp/foo'"]
rc:
    description: The return code of a USS command or MVS command, if applicable
    returned: failure
    type: int
    sample: 8
'''

import os
import tempfile
import math
import time
import stat

from pathlib import Path
from shlex import quote
from shutil import move, copy
from hashlib import sha256

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.six import PY3

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, 
    data_set_utils,
    encode_utils,
    vtoc
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport
)

try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = MissingZOAUImport()
    MVSCmd = MissingZOAUImport()
    types = MissingZOAUImport()


MVS_PARTITIONED = frozenset({'PE', 'PO', 'PDSE', 'PDS'})
MVS_SEQ = frozenset({'PS', 'SEQ'})


#TODO: Copy from local to VSAM
#TODO: Copy from remote VSAM to VSAM
#TODO: Add support for following local and remote links
#TODO: Add a 'mode' arg_type to BetterArgParser
def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='str'),
            dest=dict(required=True, type='str'),
            use_qualifier=dict(type='bool', default=False), 
            is_binary=dict(type='bool', default=False),
            is_vsam=dict(type='bool', default=False),
            encoding=dict(type='dict'),
            content=dict(type='str', no_log=True),
            backup=dict(type='bool', default=False),
            force=dict(type='bool', default=True),
            remote_src=dict(type='bool', default=False),
            checksum=dict(type='str'),
            mode=dict(type='str'),
            is_uss=dict(type='bool'),
            is_pds=dict(type='bool'),
            size=dict(type='int'),
            temp_path=dict(type='str'),
            num_files=dict(type='int'),
            copy_member=dict(type='bool')
        )
    )

    arg_def = dict(
        src=dict(arg_type='data_set_or_path', required=False),
        dest=dict(arg_type='data_set_or_path', required=True),
        is_binary=dict(arg_type='bool', required=False, default=False),
        use_qualifier=dict(arg_type='bool', required=False, default=False),
        is_vsam=dict(arg_type='bool', required=False, default=False),
        content=dict(arg_type='str', required=False),
        backup=dict(arg_type='bool', default=False, required=False),
        force=dict(arg_type='bool', default=True, required=False),
        remote_src=dict(arg_type='bool', default=False, required=False),
        checksum=dict(arg_type='str', required=False),
        mode=dict(arg_type='str', required=False)
    )

    if module.params.get("encoding"):
        module.params.update(dict(
            from_encoding=module.params.get('encoding').get('from'),
            to_encoding=module.params.get('encoding').get('to'))
        )
        arg_def.update(dict(
            from_encoding=dict(arg_type='encoding'),
            to_encoding=dict(arg_type='encoding')
        ))

    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        if (module.params.get("temp_path")):
            module.run_command("rm -r {0}".format(module.params.get("temp_path")))
        module.fail_json(
            msg="Parameter verification failed", stderr=str(err)
        )

    # ----------------------------------- X -----------------------------------

    src = parsed_args.get('src')
    b_src = to_bytes(src, errors='surrogate_or_strict')
    dest = parsed_args.get('dest')
    b_dest = to_bytes(dest, errors='surrogate_or_strict')
    remote_src = parsed_args.get('remote_src')
    use_qualifier = parsed_args.get('use_qualifier')
    is_binary = parsed_args.get('is_binary')
    is_vsam = parsed_args.get('is_vsam')
    content = parsed_args.get('content')
    force = parsed_args.get('force')
    backup = parsed_args.get('backup')
    mode = parsed_args.get('mode')
    encoding = module.params.get('encoding')
    _is_uss = module.params.get('is_uss')
    _is_pds = module.params.get('is_pds')
    _temp_path = module.params.get('temp_path')
    _size = module.params.get('size')
    _copy_member = module.params.get('copy_member')
    dest_name = dest[:dest.rfind('(')] if _copy_member else dest
    src_name = src[:src.rfind('(')] if src.endswith(')') else src
    
    if mode == 'preserve':
        mode = '0{:o}'.format(stat.S_IMODE(os.stat(b_src).st_mode))

    changed = False
    backup_path = None
    src_ds_vol = None
    res_args = dict()

    # ----------------------------------- X -----------------------------------
    try:
        if remote_src and '/' in src:
            if not os.path.exists(b_src):
                module.fail_json(msg="Source {0} does not exist".format(src))
            if not os.access(src, os.R_OK):
                module.fail_json(msg="Source {0} is not readable".format(src))

    # ----------------------------------- X -----------------------------------

        try:
            dest_ds_utils = data_set_utils.DataSetUtils(module, dest_name)
            dest_exists = dest_ds_utils.data_set_exists()
            if _is_uss:
                dest_ds_type = "USS"
            else:
                dest_ds_type = dest_ds_utils.get_data_set_type()
            if _temp_path or '/' in src:
                src_ds_type = "USS"
            else:
                src_ds_utils = data_set_utils.DataSetUtils(module, src_name)
                src_ds_type = src_ds_utils.get_data_set_type()
                src_ds_vol = src_ds_utils.get_data_set_volume()
        except Exception as err:
            module.fail_json(msg=str(err))

    # ----------------------------------- X -----------------------------------

        copy_handler = CopyHandler(module, dest_exists)
        try:
            _validate_target_type(src, dest, src_ds_type, dest_ds_type)
        except IncompatibleTargetError as err:
            module.fail_json(msg=str(err))

    # ----------------------------------- X -----------------------------------

        if dest_exists:
            if backup and dest_ds_type != "USS":
                backup_path = copy_handler.backup_data_set(dest, dest_ds_type)
        else:
            if(
                _is_pds or 
                _copy_member or 
                src_ds_type in MVS_PARTITIONED or 
                os.path.isdir(b_src)
            ):

                dest_ds_type = "PDSE"
            elif is_vsam:
                dest_ds_type = "VSAM"
            else:
                dest_ds_type = "SEQ"
            if dest_ds_type in ("PDSE", "VSAM"):
                ds_props = dict(
                    name=src,
                    volser=src_ds_vol
                )
                
                copy_handler.create_data_set(
                    src, dest_name, _size, dest_ds_type, src_ds_type, 
                    remote_src=remote_src, ds_props=ds_props
                )
            res_args['changed'] = True

    # ----------------------------------- X -----------------------------------

        if encoding:
            copy_handler.convert_encoding(_temp_path, encoding)

        if _is_uss:
            if not os.access(dest, os.W_OK):
                copy_handler._fail_json("Destination {0} is not writable".format(dest))
            if os.path.exists(dest) and os.path.isdir(dest):
                dest = os.path.join(dest, os.path.basename(src))
            try:
                remote_checksum = _get_file_checksum(_temp_path)
                dest_checksum = _get_file_checksum(dest)
            except Exception as err:
                copy_handler._fail_json(msg="Unable to calculate checksum", stderr=str(err))
            
            if mode:
                module.set_mode_if_different(src, mode, True)
            backup_path = copy_handler.copy_to_uss(
                src, _temp_path, dest, is_binary=is_binary, 
                remote_src=remote_src, backup=backup
            )
            res_args['changed'] = remote_checksum != dest_checksum
            res_args['checksum'] = remote_checksum
            res_args['size'] = Path(dest).stat().st_size
    
    # ----------------------------------- X -----------------------------------

        elif remote_src:
            copy_handler.remote_copy_handler(
                src, dest, src_ds_type, dest_ds_type, copy_member=_copy_member
            )

    # ----------------------------------- X -----------------------------------
        else:
            # Copy to sequential data set
            if dest_ds_type in MVS_SEQ:
                copy_handler.copy_to_seq(_temp_path, dest, "USS")

    # ----------------------------------- X -----------------------------------
            # Copy to partitioned data set
            elif dest_ds_type in MVS_PARTITIONED:
                temp_dir = os.path.join(_temp_path, os.path.basename(src))
                print(temp_dir)
                print(os.path.isdir(temp_dir))
                copy_handler.copy_to_pdse(temp_dir, dest, "USS", 
                copy_member=_copy_member
                )

    # ----------------------------------- X -----------------------------------
            # Copy to VSAM data set
            else:
                copy_handler.copy_to_ds(dest, size=_size)
    finally:
        if _temp_path:
            module.run_command("rm -r {0}".format(_temp_path))

    res_args.update(
        dict(
            src=src,
            dest=dest,
            ds_type = dest_ds_type,
            dest_exists=dest_exists
        )  
    )
    if backup_path:
        res_args['backup_file'] = backup_path

    module.exit_json(**res_args)


def _get_file_checksum(src):
    """ Calculate SHA256 hash for a given file """
    b_src = to_bytes(src)
    if not os.path.exists(b_src) or os.path.isdir(b_src):
        return None
    blksize = 64 * 1024
    hash_digest = sha256()
    try:
        with open(to_bytes(src, errors='surrogate_or_strict'), 'rb') as infile:
            block = infile.read(blksize)
            while block:
                hash_digest.update(block)
                block = infile.read(blksize)
    except Exception as err:
        raise
    return hash_digest.hexdigest()


def _validate_target_type(src, dest, src_type, dest_type):
    incompatible = False
    if (src_type in MVS_SEQ):
        incompatible = dest_type in MVS_PARTITIONED and not dest.endswith(')')
    elif (src_type in MVS_PARTITIONED):
        incompatible = (dest_type == "VSAM" or 
                        (src.endswith(')') and not dest.endswith(')')))
    elif (src_type == "USS"):
        pass
    else:
        incompatible = dest_type in MVS_PARTITIONED
    if incompatible:
        raise IncompatibleTargetError(src_type, dest_type)


class CopyHandler(object):
    def __init__(self, module, dest_exists):
        self.module = module
        self.dest_exists = dest_exists

    def _fail_json(self, **kwargs):
        """ Wrapper for AnsibleModule.fail_json """
        self.module.fail_json(**kwargs, dest_exists=self.dest_exists)

    def _run_command(self, cmd, **kwargs):
        """ Wrapper for AnsibleModule.run_command """
        return self.module.run_command(cmd, **kwargs)

    def copy_to_ds(self, src, dest):
        repro_cmd = "  REPRO INFILE({0}) OUTFILE({1})".format(src, dest)
        try:
            sysprint = _run_mvs_command("IDCAMS", repro_cmd, authorized=True)
        except Exception as err:
            self._fail_json(
                msg="Error while copying data from {0} to {1}".format(src, dest), 
                stderr=str(err)
        )
    
    def copy_to_uss(
        self, src, temp_path, dest, is_binary=False, remote_src=False, backup=False
    ):
        backup_path = None
        if backup:
            current_time = time.strftime("%Y-%m-%d@%I:%M~", time.localtime())
            backup_file = "{0}.{1}".format(os.path.basename(dest), current_time)
            backup_path = os.path.join(os.path.dirname(dest), backup_file)
            try:
                copy(dest, backup_path)
            except FileNotFoundError:
                pass

        if remote_src:
            if not os.path.exists(to_bytes(src)):
                module.fail_json(msg="Source {0} not found".format(src))
            if not os.access(to_bytes(src), os.R_OK):
                module.fail_json(msg="Source {0} not readable".format(src))
            try:
                copy(src, dest)
            except OSError as err:
                self._fail_json(
                    msg="Destination {0} is not writable".format(dest), 
                    stderr=str(err)
                )
        else:
            move(temp_path, dest)
        return backup_path

    def copy_to_seq(self, src, dest, src_ds_type):
        write_rc = 0
        if src_ds_type != "VSAM":
            write_rc = Datasets.copy(src, dest)
            if write_rc != 0:
                self._fail_json(
                    msg="Non-zero return code received while writing to data set {0}".format(dest),
                    rc=write_rc
                )
        else:
            self._copy_to_ds(src, dest)

    def copy_to_pdse(self, src, dest, src_ds_type, copy_member=False):
        if copy_member:
            rc = Datasets.copy(src, dest)
            if rc != 0:
                self._fail_json(
                    msg="Unable to copy to data set member {}".format(dest), 
                    rc=rc
                )
        else:
            self._clear_pdse(dest)
            if src_ds_type == "USS":
                path, dirs, files = next(os.walk(src))
                for file in files:
                    member_name = file[:file.rfind('.')] if '.' in file else file
                    rc = Datasets.copy(path + "/" + file, "{0}({1})".format(dest, member_name))
            else:
                dds = dict(OUTPUT=dest, INPUT=src)
                copy_cmd = "   COPY OUTDD=OUTPUT,INDD=((INPUT,R))"
                rc, out, err = self._run_mvs_command("IEBCOPY", copy_cmd, dds)
                if rc != 0:
                    self._fail_json(
                        msg="Unable to copy {0} to {1}".format(src, dest),
                        stdout=out, stderr=err, rc=rc,
                        stdout_lines=out.splitlines(),
                        stderr_lines=err.splitlines()
                    )

    def create_data_set(
        self, src, dest_name, size, dest_ds_type, src_ds_type, 
        remote_src=False, ds_props=None
    ):
        out = err = None
        if (dest_ds_type == "PDSE"):
            if remote_src:
                if src_ds_type in MVS_PARTITIONED:
                    rc = self._allocate_pdse(dest_name, model_ds=src)
                elif src_ds_type in MVS_SEQ:
                    rc = self._allocate_pdse(dest_name, ds_props=ds_props)
                elif os.path.isfile(src):
                    size = Path(src).stat().st_size
                    rc = self._allocate_pdse(dest_name, size=size)
                else:
                    path, dirs, files = next(os.walk(src))
                    if dirs:
                        self._fail_json(
                            msg="Subdirectory found in source directory {0}".format(src)
                        )
                    size = sum(Path(path + "/" + f).stat().st_size for f in files)
                    rc = self._allocate_pdse(dest_name, size=size)
            else:
                rc = Datasets.create(dest_name, dest_ds_type, size, "FB")
            if rc != 0:
                self._fail_json(
                    msg="Unable to allocate destination data set to copy {0}".format(src),
                    stdout=out, stderr=err, rc=rc,
                    stdout_lines=out.splitlines() if out else None,
                    stderr_lines=err.splitlines() if err else None
                )
        else:
            self._allocate_vsam(dest_name, size)

    def remote_copy_handler(
        self, src, dest, src_ds_type, dest_ds_type, copy_member=False
    ):
        if dest_ds_type in MVS_SEQ:
            self.copy_to_seq(src, dest, src_ds_type)
        elif dest_ds_type in MVS_PARTITIONED:
            self.copy_to_pdse(src, dest, src_ds_type, copy_member=copy_member)
        else:
            #TODO: Destination is a VSAM data set
            pass

    def convert_encoding(self, file_path, encoding):
        from_code_set = encoding.get("from")
        to_code_set = encoding.get("to")
        enc_utils = encode_utils.EncodeUtils(self.module)
        if os.path.isdir(file_path):
            path, dirs, files = next(os.walk(file_path))
            for file in files:
                member = path + "/" + file
                enc_utils.uss_convert_encoding(
                   member, member, from_code_set, to_code_set
                )
        else:
            enc_utils.uss_convert_encoding(
                file_path, file_path, from_code_set, to_code_set
            )

    def backup_data_set(self, ds_name, ds_type):
        temp_ds = Datasets.temp_name()
        if (ds_type in MVS_SEQ):
            rc = Datasets.copy(ds_name, temp_ds)
            if rc != 0:
                self._fail_json(
                    msg=("Non-zero error code while trying to back up"
                         "data set {0}".format(ds_name)
                    )
                )
        elif (ds_type in MVS_PARTITIONED):
            mv_rc = Datasets.move(ds_name, temp_ds)
            if mv_rc == 0:
                rc = self._allocate_pdse(ds_name, model_ds=temp_ds)
                if rc != 0:
                    self._fail_json(
                        msg="Unable to backup partitioned data set {0}".format(ds_name),
                        rc=rc
                    )
            else:
                self._fail_json(
                    msg=("Error while moving data set {0} to a "
                         "temporary data set".format(ds_name)
                        ),
                    rc=mv_rc
                )
        else:
            # TODO: Backup VSAM
            pass
        return temp_ds

    def _run_mvs_command(self, pgm, cmd, dd=None, authorized=False):
        sysprint = "sysprint"
        sysin = "sysin"
        pgm = pgm.upper()
        if pgm == "IKJEFT01":
            sysprint = "systsprt"
            sysin = "systsin"

        mvs_cmd = "mvscmd"
        if authorized:
            mvs_cmd += "auth"
        mvs_cmd += " --pgm={0} --{1}=* --{2}=stdin"
        if dd:
            for k, v in dd.items():
                mvs_cmd += " --{0}={1}".format(k, v)
        
        rc, out, err = self._run_command(
            mvs_cmd.format(pgm, sysprint, sysin), data=cmd
        )
        return rc, out, err

    def _allocate_vsam(self, ds_name, size):
        volume = "000000"
        max_size = 16777215
        allocation_size = math.ceil(size/1048576)
        
        if allocation_size > max_size:
            msg = ("Size of data exceeds maximum allowed allocation size for VSAM."
                "Maximum size allowed: {0} Megabytes, given data size: {1}"
                " Megabytes".format(max_size, allocation_size))
            self._fail_json(msg=msg)
    
        define_sysin = ''' DEFINE CLUSTER (NAME({0})  -
            VOLUMES({1})) -                           
            DATA (NAME({0}.DATA) -
            MEGABYTES({2}, 5)) -
            INDEX (NAME({0}.INDEX)) '''.format(
                                ds_name, volume, allocation_size
                            )

        try:
            rc, out, err = self._run_mvs_command("IDCAMS", define_sysin)
            if rc != 0:
                self._fail_json(
                    msg=("Non-zero return code received while trying to "
                         "allocate destination VSAM"), 
                    stderr=err,
                    stdout=out,
                    stderr_lines=err.splitlines(),
                    stdout_lines=out.splitlines(),
                    rc=rc
                )
        except Exception as err:
            self._fail_json(
                msg="Failed to call IDCAMS to allocate VSAM data set",
                stderr=str(err)    
            )

    def _allocate_pdse(self, ds_name, model_ds=None, size=None, ds_props=None):
        if model_ds:
            alloc_cmd = "  ALLOC DS('{0}') LIKE('{1}')".format(ds_name, model_ds)
            rc, out, err = self._run_mvs_command("IKJEFT01", alloc_cmd, authorized=True)
            if rc != 0:
                self._fail_json(
                    msg="Unable to allocate destination {0}".format(ds_name),
                    stdout=out, stderr=err, rc=rc,
                    stdout_lines=out.splitlines(),
                    stderr_lines=err.splitlines()
                )
            return rc

        recfm = "FB"
        lrecl = 80
        if size is None:
            volser = ds_props['volser']
            ds_vtoc = vtoc.VolumeTableOfContents(self.module)
            vtoc_info = ds_vtoc.get_data_set_entry(ds_props['name'], volser)
            tracks = int(vtoc_info.get("last_block_pointer").get("track"))
            blocks = int(vtoc_info.get("last_block_pointer").get("block"))
            blksize = int(vtoc_info.get("block_size"))
            bytes_per_trk = 56664
            size = (tracks * bytes_per_trk) + (blocks * blksize)
            recfm = vtoc_info.get("record_format") or recfm
            lrecl = int(vtoc_info.get("record_length")) or lrecl

        size = "{0}K".format(str(int(math.ceil(size/1024))))
        return Datasets.create(ds_name, "PDSE", size, recfm, "", lrecl)

    def _clear_pdse(self, data_set):
        members = Datasets.list_members(data_set + "(*)")
        if members:
            try:
                for m in members.split('\n'):
                    rc, out, err = self._run_command("mrm {0}({1})".format(data_set, m))
                    if rc != 0:
                        self._fail_json(
                            msg="Unable to delete data set member {0} from {1}".format(m, data_set),
                            rc=rc, out=out, err=err
                        )
            finally:
                self._run_command("rm /tmp/mrm.*.sysprint")


class IncompatibleTargetError(Exception):
    def __init__(self, src_type, dest_type):
        self.msg = "Incompatible target type '{0}' for source '{1}'".format(dest_type, src_type)
        super().__init__(self.msg)


def main():
    run_module()


if __name__ == '__main__':
    main()
