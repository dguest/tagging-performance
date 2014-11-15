#include "PeterPerfHists.hh"
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

namespace peter {

// ======== efficiency hists ==============

  PtEfficiency::PtEfficiency(float antib, float antiu):
    m_pass(0),
    m_fail(0),
    m_anti_b(antib),
    m_anti_u(antiu)
  {
    m_pass = new Histogram(1000, 0, 1e6, "MeV");
    m_fail = new Histogram(1000, 0, 1e6, "MeV");
  }
  PtEfficiency::~PtEfficiency() {
    delete m_pass;
    delete m_fail;
  }
  void PtEfficiency::fill(float pt, const TagTriple& disc, double weight) {
    bool pass = (ctagAntiU(disc) > m_anti_u && ctagAntiB(disc) > m_anti_b);
    if (pass){
      m_pass->fill(pt, weight);
    } else {
      m_fail->fill(pt, weight);
    }
  }
  void PtEfficiency::writeTo(H5::CommonFG& fg) {
    m_pass->write_to(fg, "pass");
    m_fail->write_to(fg, "fail");
  }

  // ====================== All hists ========================
  // (one copy for each flavor)

  Hists::Hists() :
    m_jfc_efficiency(JFC_ANTI_B_MIN, JFC_ANTI_U_MIN),
    m_jfc(0),
    m_jfit(0)
  {
    using namespace hist;
    unsigned hflag = hist::eat_nan;
    const Axis gaia_axis = {"x", N_2AX_BINS, GAIA_LOW, GAIA_HIGH, ""};

    Axis gaia_anti_b = gaia_axis;
    gaia_anti_b.name = "antiB";

    Axis gaia_anti_u = gaia_axis;
    gaia_anti_u.name = "antiU";
    m_jfc = new Histogram({gaia_anti_u, gaia_anti_b}, hflag);
    m_jfit = new Histogram({gaia_anti_u, gaia_anti_b}, hflag);
  }

  Hists::~Hists() {
    delete m_jfc;
    delete m_jfit;
  }

  void Hists::fill(const Jet& jet, double weight) {
    m_jfc->fill({ctagAntiU(jet.jfc), ctagAntiB(jet.jfc)}, weight);
    m_jfit->fill({ctagAntiU(jet.jfit), ctagAntiB(jet.jfit)}, weight);
    m_jfc_efficiency.fill(jet.pt, jet.jfc, weight);
  }

  void Hists::writeTo(H5::CommonFG& fg) {
    m_jfc->write_to(fg, "jfc");
    m_jfit->write_to(fg, "jfit");
    H5::Group eff_group(fg.createGroup("efficiency"));
    m_jfc_efficiency.writeTo(eff_group);
  }

// ====== FlavoredHists (top level) =======

  FlavoredHists::FlavoredHists(unsigned flags):
    m_flavors(4)
  {
  }

  FlavoredHists::~FlavoredHists()
  {
  }

  void FlavoredHists::fill(const Jet& jet, double weight) {
    m_flavors.at(static_cast<int>(jet.truth_label)).fill(jet, weight);
  }

  void FlavoredHists::writeTo(H5::CommonFG& fg) {
    for (Flavor flavor: {Flavor::B, Flavor::C, Flavor::U, Flavor::T}) {
      std::string name = flavorString(flavor);
      size_t index = static_cast<size_t>(flavor);
      H5::Group flav_group(fg.createGroup(name.c_str()));
      m_flavors.at(index).writeTo(flav_group);
    }
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

