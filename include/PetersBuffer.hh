// -*- c++ -*-
#ifndef PETERS_BUFFER_HH
#define PETERS_BUFFER_HH

class SmartChain;

#include <vector>
#include <string>

struct TagArrays {
  void set(SmartChain* chain, std::string prefix);
  double* pu;
  double* pc;
  double* pb;
};

class PetersBuffer {
public:
  PetersBuffer(const std::vector<std::string>& files);
  ~PetersBuffer();
  void getEntry(int);
  int size();
  int entry() const;
  void saveSetBranches(const std::string& file_name);
  int n_jets;
  double*  jet_pt;
  double*  jet_eta;
  double*  jvf;
  int*  jet_flavor_truth_label;
  TagArrays jfit;
  TagArrays jfc;

private:
  PetersBuffer(PetersBuffer&);
  PetersBuffer& operator=(PetersBuffer);
  SmartChain* m_chain;
  int m_entry;
};

#endif

