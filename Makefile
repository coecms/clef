ENV=module load conda/analysis3-23.04;
SHELL=/bin/bash

.PHONY: check test package

check test:
	${ENV} py.test --db=postgresql://clef.nci.org.au/clef test
#	${ENV} py.test --db=postgresql://clefdev.nci.org.au/clef test

package:
	${ENV} conda build . --user coecms


