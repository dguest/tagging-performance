#include "TreeBuffer.h"
#include "SmartChain.hh"
#include "TROOT.h"

void TagVectors::set(SmartChain* chain, std::string prefix) { 
  chain->SetBranch(prefix + "pu", &pu); 
  chain->SetBranch(prefix + "pc", &pc); 
  chain->SetBranch(prefix + "pb", &pb); 
}

TreeBuffer::TreeBuffer(const std::vector<std::string>& files) : 
  m_chain(0), 
  m_entry(0)
{ 
  // thanks for this line, ROOT, really. As if we needed any more proof that 
  // this framework is a complete pile of shit, you've added some cryptic
  // bullshit that we all have to add to out files to read a fucking
  // D3PD... Not even a complicated class, a fucking D3PD...
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
