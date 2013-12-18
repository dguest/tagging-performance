# makefile for SUSY ntuple skimmer
# Author: Dan Guest (dguest@cern.ch)
# Created: Wed Jul  4 15:30:40 CEST 2012

# --- set dirs
BIN          := bin
SRC          := src
INC          := include
DICT         := dict

# --- HACKS ----
CXXFLAG_HACKS := -Wno-literal-suffix #hdf5 header sets this off

# --- external dirs 
-include local.mk		# may be used to locate HDF and other libs

ifndef ND_HIST
$(error "couldn't find ND_HIST, is it defined in local.mk?")
endif
ND_HIST_INC      := $(ND_HIST)/include
ND_HIST_LIB      := $(ND_HIST)/lib

#  set search path
vpath %.o    $(BIN)
vpath %.cxx  $(SRC) 
vpath %.hh   $(INC) 
vpath %.h    $(INC) 

# --- load in root config
ROOTCFLAGS    := $(shell root-config --cflags)
ROOTLIBS      := -L$(shell root-config --libdir)
ROOTLIBS      += -lCore -lTree -lPhysics -lRIO
ROOTLDFLAGS   := $(shell root-config --ldflags)

# and py config
PY_CONFIG := python2.7-config

PY_FLAGS :=   $(shell $(PY_CONFIG) --includes)
PY_LIB   := -L$(shell $(PY_CONFIG) --prefix)/lib
PY_LIB   +=   $(shell $(PY_CONFIG) --libs)


# --- set compiler and flags (roll c options and include paths together)
CXX          := g++
CXXFLAGS     := -O2 -Wall -fPIC -I$(INC) -I$(ND_HIST_INC) -g -std=c++11
CXXFLAGS     += ${CXXFLAG_HACKS}
LIBS         := -L$(ND_HIST_LIB) -Wl,-rpath,$(ND_HIST_LIB) -lndhist
LDFLAGS      := -Wl,-no-undefined

ifdef HDF_PATH
CXXFLAGS     += -I$(HDF_PATH)/include
LIBS         += -L$(HDF_PATH)/lib -Wl,-rpath,$(HDF_PATH)/lib
endif

# --- HDF5 needed for hist saving
LIBS         += -lhdf5_cpp -lhdf5 

# rootstuff 
CXXFLAGS     += $(ROOTCFLAGS)
LDFLAGS      += $(ROOTLDFLAGS)
LIBS         += $(ROOTLIBS)

# pystuff (roll the linking options and libraries together)
PY_LDFLAGS := $(LDFLAGS)
PY_LDFLAGS += $(PY_LIB)
PY_LDFLAGS += -shared

# ---- define objects
TOBJ        := ObjectFactory.o
GEN_OBJ     := HistBuilder.o Jet.o
GEN_OBJ     += Jet2DHists.o Jet1DHists.o 
GEN_OBJ     += JetTagRescaler.o
GEN_OBJ     += BtagConfig.o RegionConfig.o Flavor.o
GEN_OBJ     += TruthJetHists.o RegionHistograms.o EventObjects.o
GEN_OBJ     += Region2dKinematicHistograms.o
GEN_OBJ     += RegionEventFilter.o 
GEN_OBJ     += OrderedJetTagFilter.o UnorderedJetTagFilter.o
GEN_OBJ     += RegionJetEfficiencyHistograms.o
GEN_OBJ     += RegionBosonPtHistograms.o
GEN_OBJ     += common_functions.o enum_converters.o
GEN_OBJ     += BtagScaler.o BtagBuffer.o
GEN_OBJ     += EventScalefactors.o
EXE_OBJ     := $(GEN_OBJ) $(TOBJ) unit-test.o
PYLIB_OBJ   := $(GEN_OBJ) $(TOBJ)

STAND_ALONE_OBJ     := $(GEN_OBJ) $(TOBJ) stand-alone.o

PY_OBJ       := _hfw.o
PY_LIB       := ../python/stop/stack/_hfw.so


ALLOBJ       := $(GEN_OBJ) $(PY_OBJ) $(TOBJ) unit-test.o

ALLOUTPUT    := $(PY_LIB) unit-test stand-alone

all: $(ALLOUTPUT) 

unit-test: $(EXE_OBJ:%=$(BIN)/%)
	@echo "linking $^ --> $@"
	@$(CXX) -o $@ $^ $(LIBS) $(LDFLAGS)

stand-alone: $(STAND_ALONE_OBJ:%=$(BIN)/%)
	@echo "linking $^ --> $@"
	@$(CXX) -o $@ $^ $(LIBS) $(LDFLAGS)

$(PY_LIB): $(PYLIB_OBJ:%=$(BIN)/%) $(PY_OBJ:%=$(BIN)/%)
	@mkdir -p $(shell dirname $(PY_LIB))
	@echo "linking $^ --> $@"
	@$(CXX) -o $@ $^ $(LIBS) $(PY_LDFLAGS)

# --------------------------------------------------

# python object compile
$(BIN)/_%.o: _%.cxx 
	@echo compiling python object $@
	@mkdir -p $(BIN)
	@$(CXX) -c $(CXXFLAGS) $(PY_FLAGS) $< -o $@ 

# compile rule
$(BIN)/%.o: %.cxx
	@echo compiling $<
	@mkdir -p $(BIN)
	@$(CXX) -c $(CXXFLAGS) $< -o $@

# use auto dependency generation
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
.PHONY : clean rmdep
CLEANLIST     = *~ *.o *.o~ *.d core 
clean:
	rm -fr $(CLEANLIST) $(CLEANLIST:%=$(BIN)/%) $(CLEANLIST:%=$(DEP)/%)
	rm -fr $(BIN) $(ALLOUTPUT) $(DICT)

rmdep: 
	rm -f $(DEP)/*.d