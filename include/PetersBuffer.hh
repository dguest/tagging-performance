// -*- c++ -*-
#ifndef PETERS_BUFFER_HH
#define PETERS_BUFFER_HH

class SmartChain;

#include <vector>
#include <string>

const int MAX_JETS = 1000;

struct TagArrays {
  void set(SmartChain* chain, std::string prefix);
  double pu[MAX_JETS];
  double pc[MAX_JETS];
  double pb[MAX_JETS];
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
  double jet_pt[MAX_JETS];
  double jet_eta[MAX_JETS];
  double jvf[MAX_JETS];
  int jet_flavor_truth_label[MAX_JETS];
  TagArrays jfit;
  TagArrays jfc;

private:
  PetersBuffer(PetersBuffer&);
  PetersBuffer& operator=(PetersBuffer);
  SmartChain* m_chain;
  int m_entry;
};

#endif

