
SUBDIRS = plugins

INSTALLDIRS = $(SUBDIRS:%=install-%)
CLEANDIRS = $(SUBDIRS:%=clean-%)
CLOBBERDIRS = $(SUBDIRS:%=clobber-%)

all: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@

install: $(INSTALLDIRS)
$(INSTALLDIRS):
	$(MAKE) -C $(@:install-%=%) install

clean: $(CLEANDIRS)
$(CLEANDIRS):
	$(MAKE) -C $(@:clean-%=%) clean

clobber: $(CLOBBERDIRS)
$(CLOBBERDIRS):
	$(MAKE) -C $(@:clobber-%=%) clobber

.PHONY: subdirs $(SUBDIRS)
.PHONY: subdirs $(INSTALLDIRS)
.PHONY: subdirs $(CLEANDIRS)
.PHONY: subdirs $(CLOBBERDIRS)
.PHONY: install clean clobber

run-tests:
	hython bin/run_tests.py

