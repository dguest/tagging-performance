# makefile for tagging performance histogram filler
# Author: Dan Guest (dguest@cern.ch)
# created: Thu Dec 19 17:34:32 EST 2013

# --- set dirs
BUILD          := build
SRC          := src
INC          := include
DICT         := dict
OUTPUT       := bin

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
GEN_OBJ     += PetersBuffer.o fillPetersHists.o PeterPerfHists.o
GEN_OBJ     += misc_func.o buildHists.o RunConfig.o
TOP_OBJ     += tag-perf-d3pd.o tag-perf-peter.o

# stuff used for the c++ executable
ALL_EXE    := tag-perf-d3pd tag-perf-peter

# phony target used to call ndhist makefile
NDHIST_DUMMY := buildndhist
TOP_LEVEL_DUMMY := top-level
EXE_DUMMY := build-exe

# --- top level command ---
all: $(TOP_LEVEL_DUMMY)
	@$(shell ./install/pysetup.py install)
	@echo "##########################"
	@echo "#### successful build ####"
	@echo "##########################"

GEN_OBJ_PATHS := $(GEN_OBJ:%=$(BUILD)/%)
TOP_OBJ_PATHS := $(TOP_OBJ:%=$(BUILD)/%)
ALL_EXE_PATHS := $(ALL_EXE:%=$(OUTPUT)/%)

# we call the dummy first, which builds the dependencies.
# _after_ these have been built we call the linking rule.
$(TOP_LEVEL_DUMMY): $(NDHIST_DUMMY) $(GEN_OBJ_PATHS) $(TOP_OBJ_PATHS)
	@$(MAKE) $(EXE_DUMMY) --no-print-directory

$(EXE_DUMMY): $(ALL_EXE_PATHS)

$(OUTPUT)/tag-perf-%: $(GEN_OBJ_PATHS) $(BUILD)/tag-perf-%.o
	@mkdir -p $(OUTPUT)
	@echo "linking $^ --> $@"
	@$(CXX) -o $@ $^ $(LIBS) $(LDFLAGS)

$(NDHIST_DUMMY):
	@$(MAKE) -C $(ND_HIST_DIR) --no-print-directory -s

# --------------------------------------------------

# compile rule
$(BUILD)/%.o: %.cxx
	@echo compiling $<
	@mkdir -p $(BUILD)
	@$(CXX) -c $(CXXFLAGS) $< -o $@

# use auto dependency generation
ALLOBJ       := $(GEN_OBJ)
DEP = $(BUILD)

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),rmdep)
include  $(ALLOBJ:%.o=$(DEP)/%.d)
endif
endif

DEPTARGSTR = -MT $(BUILD)/$*.o -MT $(DEP)/$*.d
$(DEP)/%.d: %.cxx
	@echo making dependencies for $<
	@mkdir -p $(DEP)
	@$(CXX) -MM -MP $(DEPTARGSTR) $(CXXFLAGS) $(PY_FLAGS) $< -o $@

# clean
.PHONY : clean rmdep $(NDHIST_DUMMY) $(TOP_LEVEL_DUMMY) $(EXE_DUMMY)
CLEANLIST     = *~ *.o *.o~ *.d core
clean:
	rm -fr $(CLEANLIST) $(CLEANLIST:%=$(BUILD)/%) $(CLEANLIST:%=$(DEP)/%)
	rm -fr $(BUILD) $(DICT)
	@$(MAKE) -C $(ND_HIST_DIR) clean
	@$(shell ./install/pysetup.py remove)

rmdep:
	rm -f $(DEP)/*.d