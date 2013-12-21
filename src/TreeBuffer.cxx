#include "TreeBuffer.hh"
#include "SmartChain.hh"

TreeBuffer::TreeBuffer(const std::vector<std::string>& files) : 
  m_chain(0)
{ 
  m_chain = new SmartChain("physics"); 
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
  m_chain->SetBranch(jc +  fc + "jfit_pu",	 &jet_jfit_pu);              
  m_chain->SetBranch(jc +  fc + "jfit_pb",	 &jet_jfit_pb);              
  m_chain->SetBranch(jc +  fc + "jfit_pc",	 &jet_jfit_pc);              
  m_chain->SetBranch(jc +  fc + "gaia_pu",	 &jet_gaia_pu);              
  m_chain->SetBranch(jc +  fc + "gaia_pb",	 &jet_gaia_pb);              
  m_chain->SetBranch(jc +  fc + "gaia_pc",	 &jet_gaia_pc);              
  m_chain->SetBranch(jc +  fc + "gaia_isValid",  &jet_gaia_isValid);         
  m_chain->SetBranch(jc +  fc + "jfitc_pu",	 &jet_jfitc_pu);             
  m_chain->SetBranch(jc +  fc + "jfitc_pb",	 &jet_jfitc_pb);             
  m_chain->SetBranch(jc +  fc + "jfitc_pc",      &jet_jfitc_pc);             

}

TreeBuffer::~TreeBuffer() { 
  delete m_chain; 
}

void TreeBuffer::getEntry(int entry) { 
  m_chain->GetEntry(entry); 
}
int TreeBuffer::size() { 
  return m_chain->GetEntries(); 
}
