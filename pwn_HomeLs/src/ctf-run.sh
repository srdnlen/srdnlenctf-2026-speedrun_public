#!/bin/sh
# xinetd always starts its servers in / (it has no cwd option), so set the
# working directory here before handing over to the challenge binary.
cd /home/ctf || exit 1
exec /home/ctf/vuln
