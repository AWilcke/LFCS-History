from lfcsapp import os
from datetime import datetime

def backup(database, name=None):
    now = datetime.now().timetuple()
    if not name:
        name = 'automatic-backup'

    os.popen("%s %s --clean --no-owner --no-acl  > %s/%s-%s-%s-%s-%sh%sm%ss.dump" % (os.environ['PG_DUMP_DIR'], database, os.environ['BACKUP_DIR'], name, now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))

def restore(database, backup):
    os.popen("%s %s < %s/%s" % (os.environ['PSQL_DIR'], database, os.environ['BACKUP_DIR'], backup))
    return backup.replace('%s-' % (os.environ['DB_NAME']),'')

def get_backups():
    files = [f for f in os.listdir(os.environ['BACKUP_DIR'])]
    return files

def delete_backup(backup):
    os.remove(os.path.join(os.environ['BACKUP_DIR'], backup))
