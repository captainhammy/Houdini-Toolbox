# Makefile helper for GNU make utility and Houdini-Toolbox.
#
# For more information, see $HFS/toolkit/makefiles/Makefile.gnu
#

include $(HFS)/toolkit/makefiles/Makefile.linux

ifndef INSTDIR
    INSTDIR = $(HOME)/houdini$(HOUDINI_MAJOR_RELEASE).$(HOUDINI_MINOR_RELEASE)
endif

CXXFLAGS := -std=c++11

OBJECTS = $(SOURCES:.C=.o)
OBJECTS := $(OBJECTS:.cpp=.o)

TAGINFO = $(shell (echo -n "Compiled on:" `date`"\n         by:" `whoami`@`hostname`"\n$(SESI_TAGINFO)") | sesitag -m)

%.o:		%.C
	$(CC) $(CXXFLAGS) $(OBJFLAGS) -DMAKING_DSO $(TAGINFO) \
	    $< $(OBJOUTPUT) $@

%.o:		%.cpp
	$(CC) $(CXXFLAGS) $(OBJFLAGS) -DMAKING_DSO $(TAGINFO) \
	    $< $(OBJOUTPUT)$@

$(DSONAME):	$(OBJECTS)
	$(LINK) $(LDFLAGS) $(SHAREDFLAG) $(OBJECTS) $(DSOFLAGS) \
	    $(DSOOUTPUT) $@

default:	$(DSONAME) $(APPNAME)

ifdef HELP
help:		$(HELP)
	@mkdir -p $(INSTDIR)/help/nodes/$(HELPCONTEXT)/
	@cp $(HELP) $(INSTDIR)/help/nodes/$(HELPCONTEXT)/
else
help:
endif

ifdef ICONS
icons:		$(ICONS)
	@mkdir -p $(INSTDIR)/config/Icons
	@cp $(ICONS) $(INSTDIR)/config/Icons
else
icons:
endif

ifdef SHELFTOOLS
tools: 		$(SHELFTOOLS)
	@mkdir -p $(INSTDIR)/toolbar
	@cp $(SHELFTOOLS) $(INSTDIR)/toolbar
else
tools:
endif

install:	default	help icons tools
	@mkdir -p $(INSTDIR)/dso
	@cp $(DSONAME) $(INSTDIR)/dso

clean:
	rm -f $(OBJECTS) $(APPNAME) $(DSONAME)

clobber:
	rm -f $(INSTDIR)/dso/$(DSONAME)

ifdef HELP
	rm -f $(INSTDIR)/help/nodes/$(HELPCONTEXT)/$(HELP)
endif

ifdef ICONS
	rm -f $(INSTDIR)/config/Icons/$(ICONS)
endif

ifdef SHELFTOOLS
	rm -f $(INSTDIR)/toolbar/$(SHELFTOOLS)
endif

