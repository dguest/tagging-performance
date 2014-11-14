#include "Jet.hh"
#include "TreeBuffer.hh"
#include "PetersBuffer.hh"

#include <cassert>

TagTriple::TagTriple() : pu(-999), pc(-999), pb(-999)
{
}

TagTriple::TagTriple(const TagVectors& buff, int index):
  pu(buff.pu->at(index)),
  pc(buff.pc->at(index)),
  pb(buff.pb->at(index))
{
}

TagTriple::TagTriple(const TagArrays& buff, int index):
  pu(buff.pu[index]),
  pc(buff.pc[index]),
  pb(buff.pb[index])
{
}

bool TagTriple::allNonzero() const {
  return pu && pb && pc;
}

Jet::Jet() :
  pt(-999),
  valid(false),
  truth_label(Flavor::ERROR)
{
}

Jet::Jet(const TreeBuffer& buff, int index) :
  event(buff.entry()),
  pt(buff.jet_pt->at(index)),
  eta(buff.jet_eta->at(index)),
  jvf(-999),
  valid(true),
  mv1(buff.jet_MV1->at(index)),
  mv1c(buff.jet_MV1c->at(index)),
  mv2c00(buff.jet_MV2c00->at(index)),
  mv2c10(buff.jet_MV2c10->at(index)),
  mv2c20(buff.jet_MV2c20->at(index)),
  mvb(buff.jet_MVb->at(index)),
  truth_label(getFlavor(buff.jet_flavor_truth_label->at(index))),
  gaia(buff.gaia, index),
  jfit(buff.jfit, index),
  jfc(buff.jfc, index),
  gaia_valid(buff.jet_gaia_isValid->at(index))
{
}

Jet::Jet(const PetersBuffer& buff, int index) :
  event(buff.entry()),
  pt(buff.jet_pt[index]),
  eta(buff.jet_eta[index]),
  jvf(buff.jvf[index]),
  valid(true),
  mv1(-999),
  mv1c(-999),
  mv2c00(-999),
  mv2c10(-999),
  mv2c20(-999),
  mvb(-999),
  truth_label(getFlavor(buff.jet_flavor_truth_label[index])),
  jfit(buff.jfit, index),
  jfc(buff.jfc, index),
  gaia_valid(false)
{
  assert(buff.n_jets > index);
}

Flavor Jet::getFlavor(int ftl) {
  switch(ftl) {
  case 5: return Flavor::B;
  case 4: return Flavor::C;
  case 0: return Flavor::U;
  case 15: return Flavor::T;
  default: return Flavor::ERROR;
  }
}


// ===== exceptions =====
BadJetError::BadJetError(const std::string& problem) :
  std::range_error(problem)
{
}
