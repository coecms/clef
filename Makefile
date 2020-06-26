ENV=module load conda;
SHELL=/bin/bash

.PHONY: check test package

check test:
	${ENV} py.test --db=postgresql://reidb2.nci.org.au/clef test

package:
	${ENV} conda build . --user coecms


