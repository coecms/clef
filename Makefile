ENV=module load conda;

.PHONY: check test package

check test:
	${ENV} py.test --db=postgresql://reidb2.nci.org.au/clef

package:
	${ENV} conda build . --user coecms


