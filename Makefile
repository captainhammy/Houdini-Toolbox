
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

# Quickly compile Qt icons using PySide2.
build-icons:
	pyside2-rcc -o python/ht/ui/icons.py icons/icons.qrc


run-tests:
	hython bin/run_tests.py

