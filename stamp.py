#! /usr/bin/python
# Author: Adam Henry, @adlhenry

import os.path, re, argparse, sys
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(
	description='''Time stamps a file with a "$Id: - - $" tag.
	Updates time and version number if the file modification time
	is newer than the last time-stamp.''')
parser.add_argument('filename', nargs='+', help='Name of the file to be time-stamped.')
args = parser.parse_args()

# Program name
prog_name = os.path.basename(sys.argv[0])

# Exit status
exit_status = 0

# Regex objects
s_tag = re.compile('\$Id:.*\- \- \$')
v_tag = re.compile('\.(.*)')

# Print a warning to stderr
def warn (error_string):
	print(prog_name + ': error:', error_string, file=sys.stderr)

# Open a file
def open_file (filename, mode):
	try:
		return open(filename, mode)
	except:
		warn('cannot open file: ' + filename)
		exit_status = 1
		return -1

# Return file modification date
def mod_date (filename):
	mtime = os.path.getmtime(filename)
	return datetime.fromtimestamp(mtime)

# Update the time stamp
def update_stamp (stamp, filename):
	filename = os.path.basename(filename)
	stamp = stamp.split()
	c_date = datetime.now() + timedelta(seconds = 1)
	c_date = c_date.strftime('%Y-%m-%d %H:%M:%S')
	if (len(stamp) < 8) or (stamp[1].find(filename) == -1):
		return '$Id: ' + filename + ',v 1.0 ' + c_date + ' - - $'
	version = stamp[2]
	date_time = stamp[3] + ' ' + stamp[4]
	m_date = mod_date(filename)
	s_date = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
	if (m_date - s_date).total_seconds() > 0:
		patch = v_tag.search(version)
		patch = int(patch.group(1)) + 1
		version = v_tag.sub('.' + str(patch), version)
		return '$Id: ' + filename + ',v ' + version + ' ' + c_date + ' - - $'
	return None

# Check the time stamp
def check_stamp (filename):
	f = open_file(filename, 'r')
	if f == -1: return
	file = f.read()
	f.close()
	match = s_tag.search(file)
	if match is not None:
		new_stamp = update_stamp(match.group(), filename)
		if new_stamp is not None:
			file = s_tag.sub(new_stamp, file)
			f = open_file(filename, 'w')
			if f == -1: return
			f.write(file)
			f.close()

# Check each file
for filename in args.filename:
	check_stamp(filename)
sys.exit(exit_status)
