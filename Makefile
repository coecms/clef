ENV=module load conda;
SHELL=/bin/bash

.PHONY: check test package

check test:
	${ENV} py.test --db=postgresql://150.203.254.112/clef test

package:
	${ENV} conda build . --user coecms


