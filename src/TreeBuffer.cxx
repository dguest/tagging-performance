#include "TreeBuffer.h"
#include "SmartChain.hh"
#include "TROOT.h"
#include <fstream> // ofstream

void TagVectors::set(SmartChain* chain, std::string prefix) { 
  chain->SetBranch(prefix + "pu", &pu); 
  chain->SetBranch(prefix + "pc", &pc); 
  chain->SetBranch(prefix + "pb", &pb); 
}

TreeBuffer::TreeBuffer(const std::vector<std::string>& files) : 
  m_chain(0), 
  m_entry(0)
{ 
  // ROOT doesn't know about vectors in TTrees by default. 
  // The more complicated cases are covered by the LinkDef.h file, but basic
  // vectors must be loaded here. 
  gROOT->ProcessLine("#include <vector>");

  m_chain = new SmartChain("physics"); 
  for (auto file: files) { 
    m_chain->add(file); 
  }

  std::string jc = "jet_AntiKt4LCTopo_"; 
  std::string fc = "flavor_component_"; 
  std::string fw = "flavor_weight_"; 
  m_chain->SetBranch(jc + "pt",                  &jet_pt);
  m_chain->SetBranch(jc + "eta",                 &jet_eta);                  
  m_chain->SetBranch(jc + fw + "MV1", 		 &jet_MV1);                  
  m_chain->SetBranch(jc + fw + "MV1c", 		 &jet_MV1c);                 
  m_chain->SetBranch(jc + fw + "MV2c00", 	 &jet_MV2c00);               
  m_chain->SetBranch(jc + fw + "MV2c10", 	 &jet_MV2c10);               
  m_chain->SetBranch(jc + fw + "MV2c20",	 &jet_MV2c20);               
  m_chain->SetBranch(jc + fw + "MVb",		 &jet_MVb);                  
  m_chain->SetBranch(jc + "flavor_truth_label",	 &jet_flavor_truth_label);   
  gaia.set(m_chain, jc + fc + "gaia_"); 
  jfit.set(m_chain, jc + fc + "jfit_"); 
  jfc.set(m_chain, jc + fc + "jfitc_"); 
  m_chain->SetBranch(jc +  fc + "gaia_isValid",  &jet_gaia_isValid);         
}

TreeBuffer::~TreeBuffer() { 
  delete m_chain; 
}

void TreeBuffer::getEntry(int entry) { 
  m_entry = entry; 
  m_chain->GetEntry(entry); 
}
int TreeBuffer::size() { 
  return m_chain->GetEntries(); 
}

int TreeBuffer::entry() const { 
  return m_entry; 
}

void TreeBuffer::saveSetBranches(const std::string& file_name) { 
  std::ofstream out_file(file_name); 
  for (auto br_name: m_chain->get_all_branch_names()) { 
    out_file << br_name << "\n"; 
  }
}
