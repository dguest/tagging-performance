#include "PetersBuffer.hh"
#include "SmartChain.hh"
#include "TROOT.h"
#include <fstream> // ofstream

void TagArrays::set(SmartChain* chain, std::string prefix) {
  chain->SetBranch(prefix + "pu", &pu);
  chain->SetBranch(prefix + "pc", &pc);
  chain->SetBranch(prefix + "pb", &pb);
}

PetersBuffer::PetersBuffer(const std::vector<std::string>& files) :
  m_chain(0),
  m_entry(0)
{
  m_chain = new SmartChain("antikt4lctopo/FlavorTagging");
  for (auto file: files) {
    m_chain->add(file);
  }

  std::string jc = "jet_";
  std::string fc = "flavor_component_";
  m_chain->SetBranch("nJets",                    &n_jets);
  m_chain->SetBranch(jc + "pt",                  &jet_pt);
  m_chain->SetBranch(jc + "eta",                 &jet_eta);
  m_chain->SetBranch(jc + "JVF",                 &jvf);
  m_chain->SetBranch(jc + "flavor_truth_label",	 &jet_flavor_truth_label);
  jfit.set(m_chain, jc + fc + "jfit_");
  jfc.set(m_chain, jc + fc + "jfitc_");
}

PetersBuffer::~PetersBuffer() {
  delete m_chain;
}

void PetersBuffer::getEntry(int entry) {
  m_entry = entry;
  m_chain->GetEntry(entry);
}
int PetersBuffer::size() {
  return m_chain->GetEntries();
}

int PetersBuffer::entry() const {
  return m_entry;
}

void PetersBuffer::saveSetBranches(const std::string& file_name) {
  std::ofstream out_file(file_name);
  for (auto br_name: m_chain->get_all_branch_names()) {
    out_file << br_name << "\n";
  }
}
