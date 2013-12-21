#ifndef TREE_BUFFER_HH
#define TREE_BUFFER_HH

class SmartChain; 

#include <vector> 
#include <string> 

class TreeBuffer { 
public: 
  TreeBuffer(const std::vector<std::string>& files); 
  ~TreeBuffer(); 
  TreeBuffer(TreeBuffer&) = delete; 
  TreeBuffer& operator=(TreeBuffer) = delete; 
  void getEntry(int); 
  int size(); 
  std::vector<float>*  jet_pt; 
  std::vector<float>*  jet_eta; 
  std::vector<float>*  jet_MV1; 
  std::vector<float>*  jet_MV1c; 
  std::vector<float>*  jet_MV2c00; 
  std::vector<float>*  jet_MV2c10; 
  std::vector<float>*  jet_MV2c20;
  std::vector<float>*  jet_MVb;
  std::vector<int>  *  jet_flavor_truth_label;
  std::vector<float>*  jet_jfit_pu;
  std::vector<float>*  jet_jfit_pb;
  std::vector<float>*  jet_jfit_pc;
  std::vector<float>*  jet_gaia_pu;
  std::vector<float>*  jet_gaia_pb;
  std::vector<float>*  jet_gaia_pc;
  std::vector<int>  *  jet_gaia_isValid; 
  std::vector<float>*  jet_jfitc_pu;
  std::vector<float>*  jet_jfitc_pb;
  std::vector<float>*  jet_jfitc_pc;             

private: 
  SmartChain* m_chain; 
}; 

#endif 

