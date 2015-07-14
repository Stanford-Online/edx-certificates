#!/usr/bin/make -F

watch:
	./openedx_certificates/bin/watch.py

clean:
	find openedx_certificates -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	-rm *.pyc
	rm -rf ./htmlcov
