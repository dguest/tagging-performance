#ifndef JET_PERF_HISTS_HH
#define JET_PERF_HISTS_HH

class Histogram; 
class Jet; 
namespace H5 { 
  class CommonFG; 
}

#include <vector> 

namespace hist { 
  const int N_BINS = 10000; 
  const int N_2AX_BINS = 1000; 
  const double GAIA_LOW = -10.0; 
  const double GAIA_HIGH = 10.0; 
}

class BtagHists { 
public: 
  BtagHists(); 
  ~BtagHists(); 
  BtagHists(BtagHists&) = delete; 
  BtagHists& operator=(BtagHists&) = delete; 
  void fill(const Jet&, double weight); 
  void writeTo(H5::CommonFG&); 
private: 
  Histogram* m_mv1; 
  Histogram* m_gaia_anti_light; 
  Histogram* m_gaia_anti_charm; 
  Histogram* m_mv2c00; 
  Histogram* m_mv2c20; 
}; 

class FlavoredHists { 
public: 
  void fill(const Jet&, double weight); 
  void writeTo(H5::CommonFG&); 
private: 
  BtagHists m_btag; 
}; 

class JetPerfHists { 
public: 
  JetPerfHists(); 
  ~JetPerfHists(); 
  JetPerfHists(JetPerfHists&) = delete; 
  JetPerfHists& operator=(JetPerfHists&) = delete; 
  void fill(const Jet&, double weight); 
  void writeTo(H5::CommonFG&); 
private: 
  std::vector<FlavoredHists> m_flavors; 
}; 

#endif
