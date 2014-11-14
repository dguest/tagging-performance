# makefile for tagging performance histogram filler
# Author: Dan Guest (dguest@cern.ch)
# created: Thu Dec 19 17:34:32 EST 2013

# --- set dirs
BIN          := build
SRC          := src
INC          := include
DICT         := dict
OUTPUT       := scripts

# --- HACKS ----
CXXFLAG_HACKS := -Wno-literal-suffix #hdf5 header sets this off

#  set search path
vpath %.cxx  $(SRC)
vpath %.hh   $(INC)
vpath %.h    $(INC)
vpath %Dict.h $(DICT)
vpath %Dict.cxx $(DICT)

# --- hdf and ndhist
HDF_INFO := $(shell h5c++ -showconfig | grep 'Installation point:')
HDF_PATH := $(strip $(shell echo ${HDF_INFO} | cut -d ':' -f 2 ))
ifndef HDF_PATH
$(error "couldn't find HDF, quitting")
endif

ND_HIST_DIR      := $(CURDIR)/ndhist
ND_HIST_INC      := $(ND_HIST_DIR)/include
ND_HIST_LIB      := $(ND_HIST_DIR)/lib

# --- load in root config
ROOTCFLAGS    := $(shell root-config --cflags)
# would be nice to avoid linking everything, but that will probably cause
# problems...
ROOTLIBS      := $(shell root-config --libs)
# ROOTLIBS      := -L$(shell root-config --libdir)
# ROOTLIBS      += -lCore -lTree -lRIO
# ROOTLIBS      += -lCint		# don't know why we need this...
ROOTLDFLAGS   := $(shell root-config --ldflags)

# --- set compiler and flags (roll c options and include paths together)
CXX          ?= g++
CXXFLAGS     := -O2 -Wall -fPIC -I$(INC) -I$(ND_HIST_INC) -g -std=c++11
CXXFLAGS     += $(CXXFLAG_HACKS)
LIBS         := -L$(ND_HIST_LIB) -Wl,-rpath,$(ND_HIST_LIB) -lndhist
LDFLAGS      := #-Wl,--no-undefined

CXXFLAGS     += -I$(HDF_PATH)/include
LIBS         += -L$(HDF_PATH)/lib -Wl,-rpath,$(HDF_PATH)/lib

# --- HDF5 needed for hist saving
LIBS         += -lhdf5_cpp -lhdf5

# --- rootstuff
CXXFLAGS     += $(ROOTCFLAGS)
LDFLAGS      += $(ROOTLDFLAGS)
LIBS         += $(ROOTLIBS)

# ---- define objects
GEN_OBJ     := SmartChain.o JetPerfHists.o Jet.o TreeBuffer.o
GEN_OBJ     += PetersBuffer.o
GEN_OBJ     += misc_func.o buildHists.o

# stuff used for the c++ executable
STAND_ALONE_OBJ     := $(GEN_OBJ) stand-alone.o
STAND_ALONE_NAME  := tag-perf-hists
STAND_ALONE    := $(OUTPUT)/$(STAND_ALONE_NAME)

# phony target used to call ndhist makefile
NDHIST_DUMMY := buildndhist
STAND_ALONE_DUMMY := build-stand-alone

# --- top level command ---
all: $(STAND_ALONE_DUMMY)
	@$(shell ./install/pysetup.py install)
	@echo "##########################"
	@echo "#### successful build ####"
	@echo "##########################"

STAND_ALONE_OBJ_PATHS := $(STAND_ALONE_OBJ:%=$(BIN)/%)

# we call the dummy first, which builds the dependencies.
# _after_ these have been built we call the linking rule.
$(STAND_ALONE_DUMMY): $(NDHIST_DUMMY) $(STAND_ALONE_OBJ_PATHS)
	@$(MAKE) $(STAND_ALONE) --no-print-directory

$(STAND_ALONE): $(STAND_ALONE_OBJ_PATHS)
	@mkdir -p $(OUTPUT)
	@echo "linking $^ --> $@"
	@$(CXX) -o $@ $^ $(LIBS) $(LDFLAGS)

$(NDHIST_DUMMY):
	@$(MAKE) -C $(ND_HIST_DIR) --no-print-directory -s

# --------------------------------------------------

# compile rule
$(BIN)/%.o: %.cxx
	@echo compiling $<
	@mkdir -p $(BIN)
	@$(CXX) -c $(CXXFLAGS) $< -o $@

# use auto dependency generation
ALLOBJ       := $(GEN_OBJ)
DEP = $(BIN)

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),rmdep)
include  $(ALLOBJ:%.o=$(DEP)/%.d)
endif
endif

DEPTARGSTR = -MT $(BIN)/$*.o -MT $(DEP)/$*.d
$(DEP)/%.d: %.cxx
	@echo making dependencies for $<
	@mkdir -p $(DEP)
	@$(CXX) -MM -MP $(DEPTARGSTR) $(CXXFLAGS) $(PY_FLAGS) $< -o $@

# clean
.PHONY : clean rmdep $(NDHIST_DUMMY) $(STAND_ALONE_DUMMY)
CLEANLIST     = *~ *.o *.o~ *.d core
clean:
	rm -fr $(CLEANLIST) $(CLEANLIST:%=$(BIN)/%) $(CLEANLIST:%=$(DEP)/%)
	rm -fr $(BIN) $(DICT) $(STAND_ALONE)
	@$(MAKE) -C $(ND_HIST_DIR) clean
	@$(shell ./install/pysetup.py remove)

rmdep:
	rm -f $(DEP)/*.d