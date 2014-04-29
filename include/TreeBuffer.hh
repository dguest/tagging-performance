// -*- c++ -*-
#ifndef TREE_BUFFER_HH
#define TREE_BUFFER_HH

class SmartChain;

#include <vector>
#include <string>

struct TagVectors {
  void set(SmartChain* chain, std::string prefix);
  std::vector<float>* pu;
  std::vector<float>* pc;
  std::vector<float>* pb;
};

class TreeBuffer {
public:
  TreeBuffer(const std::vector<std::string>& files);
  ~TreeBuffer();
  void getEntry(int);
  int size();
  int entry() const;
  void saveSetBranches(const std::string& file_name);
  std::vector<float>*  jet_pt;
  std::vector<float>*  jet_eta;
  std::vector<float>*  jet_MV1;
  std::vector<float>*  jet_MV1c;
  std::vector<float>*  jet_MV2c00;
  std::vector<float>*  jet_MV2c10;
  std::vector<float>*  jet_MV2c20;
  std::vector<float>*  jet_MVb;
  std::vector<int>  *  jet_flavor_truth_label;
  TagVectors gaia;
  TagVectors jfit;
  TagVectors jfc;
  std::vector<int>  *  jet_gaia_isValid;

private:
  TreeBuffer(TreeBuffer&);
  TreeBuffer& operator=(TreeBuffer);
  SmartChain* m_chain;
  int m_entry;
};

#endif

