#ifndef JET_PERF_HISTS_HH
#define JET_PERF_HISTS_HH

class Histogram; 
class Jet; 
namespace H5 { 
  class CommonFG; 
}

#include <vector> 
#include <map>
#include <cstddef>		// size_t

namespace hist { 
  const int N_BINS = 10000; 
  const int N_2AX_BINS = 2000; 
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
  Histogram* m_mv1c; 
  Histogram* m_gaia_anti_light; 
  Histogram* m_gaia_anti_charm; 
  Histogram* m_gaia_gr1; 
  Histogram* m_mv2c00; 
  Histogram* m_mv2c10; 
  Histogram* m_mv2c20; 
}; 

class CtagHists { 
public: 
  CtagHists(); 
  ~CtagHists(); 
  CtagHists(CtagHists&) = delete; 
  CtagHists& operator=(CtagHists&) = delete; 
  void fill(const Jet&, double weight); 
  void writeTo(H5::CommonFG&); 
private: 
  Histogram* m_gaia; 
  Histogram* m_jfc; 
  Histogram* m_jfit; 
  Histogram* m_gaia_c; 
}; 

class FlavoredHists { 
public: 
  FlavoredHists(); 
  void fill(const Jet&, double weight); 
  void writeTo(H5::CommonFG&); 
private: 
  BtagHists m_btag; 
  CtagHists m_ctag; 
  std::vector<BtagHists> m_pt_btag; 
  std::map<double, size_t> m_pt_bins; 
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
