#include "JetPerfHists.hh"
#include "Jet.hh"
#include "Histogram.hh"

#include "H5Cpp.h"

#include <stdexcept> 
#include <cmath>

namespace {
  double btagAntiU(const TagTriple&); 
  double btagAntiC(const TagTriple&); 
  std::string flavorString(Flavor); 
} 

// ======== btag hists ==============

BtagHists::BtagHists() : 
  m_mv1(0), 
  m_gaia_anti_light(0), 
  m_gaia_anti_charm(0), 
  m_mv2c00(0), 
  m_mv2c20(0)
{
  using namespace hist; 
  m_mv1 = new Histogram(N_BINS, 0.0, 1.0); 
  m_gaia_anti_light = new Histogram(N_BINS, GAIA_LOW, GAIA_HIGH); 
  m_gaia_anti_charm = new Histogram(N_BINS, GAIA_LOW, GAIA_HIGH); 
  m_mv2c00 = new Histogram(N_BINS, 0.0, 1.0); 
  m_mv2c20 = new Histogram(N_BINS, 0.0, 1.0); 
}

BtagHists::~BtagHists() { 
  delete m_mv1; 
  delete m_gaia_anti_light; 
  delete m_mv2c00; 
  delete m_mv2c20; 
}

void BtagHists::fill(const Jet& jet, double weight) { 
  m_mv1->fill(jet.mv1, weight); 
  m_gaia_anti_light->fill(btagAntiC(jet.gaia), weight); 
  m_gaia_anti_charm->fill(btagAntiU(jet.gaia), weight); 
  m_mv2c00->fill(jet.mv2c00, weight); 
  m_mv2c20->fill(jet.mv2c20, weight); 
}

void BtagHists::writeTo(H5::CommonFG& fg) { 
  m_mv1->write_to(fg, "mv1"); 
  m_gaia_anti_light->write_to(fg, "gaiaAntiU"); 
  m_gaia_anti_charm->write_to(fg, "gaiaAntiC"); 
  m_mv2c00->write_to(fg, "mv2c00"); 
  m_mv2c20->write_to(fg, "mv2c20"); 
}

// ============ flavored hists ================

void FlavoredHists::fill(const Jet& jet, double weight) { 
  m_btag.fill(jet, weight); 
}

void FlavoredHists::writeTo(H5::CommonFG& fg) { 
  H5::Group btag_group(fg.createGroup("btag")); 
  m_btag.writeTo(btag_group); 
}

// ====== JetPerfHists (top level) =======

JetPerfHists::JetPerfHists(): 
  m_flavors(4)
{ 
}

JetPerfHists::~JetPerfHists() 
{ 
}

void JetPerfHists::fill(const Jet& jet, double weight) { 
  m_flavors.at(static_cast<int>(jet.truth_label)).fill(jet, weight); 
}

void JetPerfHists::writeTo(H5::CommonFG& fg) { 
  for (Flavor flavor: {Flavor::B, Flavor::C, Flavor::U, Flavor::T}) { 
    std::string name = flavorString(flavor); 
    size_t index = static_cast<size_t>(flavor); 
    H5::Group flav_group(fg.createGroup(name)); 
    m_flavors.at(index).writeTo(flav_group); 
  }
}

namespace {
  double btagAntiU(const TagTriple& tr) { 
    return log(tr.pb / tr.pu); 
  }
  double btagAntiC(const TagTriple& tr) { 
    return log(tr.pb / tr.pc); 
  }
  
  std::string flavorString(Flavor flavor) { 
    switch (flavor) { 
    case Flavor::U: return "U"; 
    case Flavor::B: return "B"; 
    case Flavor::C: return "C"; 
    case Flavor::T: return "T"; 
    default: throw std::domain_error("what the fuck his that..."); 
    }
  }
} 
