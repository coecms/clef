ENV=module load conda;

.PHONY: check test package

check test:
	${ENV} py.test --db=postgresql://clef.nci.org.au/postgres

package:
	${ENV} conda build . --user coecms


