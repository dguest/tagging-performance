#include "JetPerfHists.hh"
#include "Jet.hh"
#include "Histogram.hh"

#include "H5Cpp.h"

#include <stdexcept> 
#include <cmath>
#include <cassert> 
#include <limits>

namespace {
  double btagAntiU(const TagTriple&); 
  double btagAntiC(const TagTriple&); 
  double ctagAntiB(const TagTriple& tr); 
  double ctagAntiU(const TagTriple& tr);  
  double gr1(const TagTriple&); 
  std::string flavorString(Flavor); 
  std::string binString(double); 
} 

// ======== btag hists ==============

BtagHists::BtagHists() : 
  m_mv1(0), 
  m_mv1c(0), 
  m_gaia_anti_light(0), 
  m_gaia_anti_charm(0), 
  m_gaia_gr1(0), 
  m_mv2c00(0), 
  m_mv2c10(0), 
  m_mv2c20(0)
{
  using namespace hist; 
  unsigned hflag = hist::eat_nan; 
  const Axis mv1_axis = {"x", N_BINS, 0.0, 1.0, ""}; 
  const Axis mv2_axis = {"x", N_BINS, -1.0, 1.0, ""}; 
  const Axis gaia_axis = {"x", N_BINS, GAIA_LOW, GAIA_HIGH, ""}; 
  m_mv1 = new Histogram({mv1_axis}, hflag); 
  m_mv1c = new Histogram({mv1_axis}, hflag); 
  m_gaia_anti_light = new Histogram({gaia_axis}, hflag); 
  m_gaia_anti_charm = new Histogram({gaia_axis}, hflag); 
  m_gaia_gr1 = new Histogram({gaia_axis}, hflag); 
  m_mv2c00 = new Histogram({mv2_axis}, hflag); 
  m_mv2c10 = new Histogram({mv2_axis}, hflag); 
  m_mv2c20 = new Histogram({mv2_axis}, hflag); 
}

BtagHists::~BtagHists() { 
  delete m_mv1; 
  delete m_mv1c; 
  delete m_gaia_anti_light; 
  delete m_gaia_anti_charm; 
  delete m_gaia_gr1; 
  delete m_mv2c00; 
  delete m_mv2c10; 
  delete m_mv2c20; 
}

void BtagHists::fill(const Jet& jet, double weight) { 
  m_mv1->fill(jet.mv1, weight); 
  m_mv1c->fill(jet.mv1c, weight); 
  m_gaia_anti_light->fill(btagAntiU(jet.gaia), weight); 
  m_gaia_anti_charm->fill(btagAntiC(jet.gaia), weight); 
  m_gaia_gr1->fill(gr1(jet.gaia), weight); 
  m_mv2c00->fill(jet.mv2c00, weight); 
  m_mv2c10->fill(jet.mv2c10, weight); 
  m_mv2c20->fill(jet.mv2c20, weight); 
}

void BtagHists::writeTo(H5::CommonFG& fg) { 
  m_mv1->write_to(fg, "mv1"); 
  m_mv1c->write_to(fg, "mv1c"); 
  m_gaia_anti_light->write_to(fg, "gaiaAntiU"); 
  m_gaia_anti_charm->write_to(fg, "gaiaAntiC"); 
  m_gaia_gr1->write_to(fg, "gaiaGr1"); 
  m_mv2c00->write_to(fg, "mv2c00"); 
  m_mv2c10->write_to(fg, "mv2c10"); 
  m_mv2c20->write_to(fg, "mv2c20"); 
}

// ======== charm tag hists ==============

CtagHists::CtagHists() : 
  m_gaia(0), 
  m_jfc(0), 
  m_jfit(0), 
  m_gaia_c(0)
{
  using namespace hist; 
  unsigned hflag = hist::eat_nan; 
  const Axis gaia_axis = {"x", N_2AX_BINS, GAIA_LOW, GAIA_HIGH, ""}; 

  Axis gaia_anti_b = gaia_axis; 
  gaia_anti_b.name = "antiB"; 

  Axis gaia_anti_u = gaia_axis; 
  gaia_anti_u.name = "antiU"; 
  m_gaia = new Histogram({gaia_anti_u, gaia_anti_b}, hflag); 
  m_jfc = new Histogram({gaia_anti_u, gaia_anti_b}, hflag); 
  m_jfit = new Histogram({gaia_anti_u, gaia_anti_b}, hflag); 
  m_gaia_c = new Histogram(N_BINS, 0.0, 1.0, "", hflag); 
}

CtagHists::~CtagHists() { 
  delete m_gaia; 
  delete m_jfc; 
  delete m_jfit; 
  delete m_gaia_c; 
}

void CtagHists::fill(const Jet& jet, double weight) { 
  m_gaia->fill({ctagAntiU(jet.gaia), ctagAntiB(jet.gaia)}, weight); 
  m_jfc->fill({ctagAntiU(jet.jfc), ctagAntiB(jet.jfc)}, weight); 
  m_jfit->fill({ctagAntiU(jet.jfit), ctagAntiB(jet.jfit)}, weight); 
  m_gaia_c->fill(jet.gaia.pc, weight); 
}

void CtagHists::writeTo(H5::CommonFG& fg) { 
  m_gaia->write_to(fg, "gaia"); 
  m_jfc->write_to(fg, "jfc"); 
  m_jfit->write_to(fg, "jfit"); 
  m_gaia_c->write_to(fg, "gaiaC"); 
}


// ============ flavored hists ================

FlavoredHists::FlavoredHists(): 
  m_pt_btag(12)
{ 
  static_assert(std::numeric_limits<double>::has_infinity, "no infinity"); 
  const std::vector<double> pt_bins_gev{
    0, 20, 30, 40, 50, 60, 75, 90, 110, 150, 200, 600, 
      std::numeric_limits<double>::infinity()}; 
  // upper_bound should never pick the bin with upper edge 20
  size_t bin = -1; 
  for (auto pt: pt_bins_gev) { 
    m_pt_bins[pt * 1e3] = bin; 
    bin++; 
  }
}

void FlavoredHists::fill(const Jet& jet, double weight) { 
  m_btag.fill(jet, weight); 
  m_ctag.fill(jet, weight); 
  auto pt_itr = m_pt_bins.upper_bound(jet.pt); 
  if (pt_itr != m_pt_bins.end()) { 
    m_pt_btag.at(pt_itr->second).fill(jet, weight); 
  }
}

void FlavoredHists::writeTo(H5::CommonFG& fg) { 
  H5::Group btag_group(fg.createGroup("btag")); 
  H5::Group all_pt(btag_group.createGroup("all")); 
  m_btag.writeTo(all_pt); 

  H5::Group ctag_group(fg.createGroup("ctag")); 
  H5::Group all_pt_ctag(ctag_group.createGroup("all")); 
  m_ctag.writeTo(all_pt_ctag); 

  H5::Group pt_bins(btag_group.createGroup("ptBins")); 
  std::string last_bin = "NONE"; 
  for (auto pt_itr: m_pt_bins) { 
    std::string bin_high = binString(pt_itr.first); 
    if ( (pt_itr.second >= 0) && (pt_itr.second < m_pt_bins.size() )) { 
      auto bin_name = last_bin + "-" + bin_high; 
      H5::Group this_bin(pt_bins.createGroup(bin_name)); 
      auto& pt_hist = m_pt_btag.at(pt_itr.second); 
      pt_hist.writeTo(this_bin); 
    }
    last_bin = bin_high; 
  }
  
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

  double ctagAntiB(const TagTriple& tr) { 
    return log(tr.pc / tr.pb); 
  }
  double ctagAntiU(const TagTriple& tr) { 
    return log(tr.pc / tr.pu); 
  }

  double gr1(const TagTriple& tr) { 
    return log(tr.pb / sqrt(tr.pc * tr.pu)); 
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
  std::string binString(double val) { 
    return std::isinf(val) ? "INF" : std::to_string(int(val) / 1000); 
  }
} 

