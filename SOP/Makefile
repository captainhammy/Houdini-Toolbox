
SUBDIRS = SOP_IdAttribCopy \
	  SOP_IdBlast \
	  SOP_PointsFromVoxels \
	  SOP_PrimCentroid \
	  SOP_PrimGroupCentroid \
	  SOP_Varmap

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

