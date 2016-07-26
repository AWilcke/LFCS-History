from lfcsapp import os
from datetime import datetime

#create a backup of specified database, output with a specified name
def backup(database, name=None):
    now = datetime.now().timetuple()
    #make sure name has proper format
    if name:
        name = name.replace(' ','-').replace('_','-')
    else:
        name = 'automatic-backup'

    os.popen("%s %s --clean --no-owner --no-acl  > %s/%s_%s-%s-%s-%sh%sm%ss.dump" % (os.environ['PG_DUMP_DIR'], database, os.environ['BACKUP_DIR'], name, now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))

#restore specified database from backup, return name of backup that was restored
def restore(database, backup):
    os.popen("%s %s < %s/%s" % (os.environ['PSQL_DIR'], database, os.environ['BACKUP_DIR'], backup))
    return backup

#return list of all backups
def get_backups():
    files = [f for f in os.listdir(os.environ['BACKUP_DIR'])]
    return files

#delete specified backup
def delete_backup(backup):
    os.remove(os.path.join(os.environ['BACKUP_DIR'], backup))

#clean backups, only keeping relevant ones
#every backup of today, one per day of last week and one per previous month
def clean_backups():
    backups = get_backups()
    now = datetime.now()
    this_week = []
    today = []
    others = {}
    #filter into today, this week, and older
    for backup in backups:
        time = datetime.strptime(backup.split('_')[1], '%d-%m-%Y-%Hh%Mm%Ss.dump')
        if 7>(now-time).days>0:
            this_week.append(backup)
        elif (now-time).days==0:
            today.append(backup)
        else:
            month = (now-time).days/30
            if others.has_key(month): others[month].append(backup)
            else:
                others[month] = [backup]
    #filter this week into days
    days = {}
    for backup in this_week:
        time = datetime.strptime(backup.split('_')[1], '%d-%m-%Y-%Hh%Mm%Ss.dump')
        if days.has_key((now-time).days):
            days[(now-time).days].append(backup)
        else:
            days[(now-time).days] = [backup]

    #keep one backup per month
    for month in others.keys():
        for backup in others[month][:-1]:
            delete_backup(backup)
    #keep one backup per day for a week
    for day in days.keys():
        for backup in days[day][:-1]:
            delete_backup(backup)


