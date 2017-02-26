#!/bin/bash
# DjZU
# Run BS440webapp.py
# Put the following line (remove the # and replace path/to) in your /etc/rc.local to run the Flask web app at boot time
#/path/to/BS440/plugins/BS440webapp/BS440webapp.sh >/dev/null 2>&1 &

execPath="$(dirname $0)"
log="$execPath""/BS440flask.log"
[ -e "$log" ] || touch "$log"

cd "$execPath""/"
"$execPath""/BS440flask.py" &

exitCode="$?"
if [[ "$exitCode" != "0" ]]; then
	 echo "$(LC_ALL=en_EN.utf8 date +"%a, %d %b %Y %H:%M:%S")	ERROR	Failed starting BS440flask.py during boot time. Exit code was $exitCode." >> "$log"
fi

exit 0

