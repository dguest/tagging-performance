#ifndef JET_PERF_HISTS_HH
#define JET_PERF_HISTS_HH

class Histogram; 
class Jet; 
namespace H5 { 
  class CommonFG; 
}

// class FlavorArray { 
//   FlavorArray(
// }; 

class JetPerfHists { 
public: 
  JetPerfHists(); 
  ~JetPerfHists(); 
  JetPerfHists(JetPerfHists&) = delete; 
  JetPerfHists* operator=(JetPerfHists&) = delete; 
  void fill(const Jet&); 
  void write_to(H5::CommonFG&); 
private: 
  
}; 

#endif
