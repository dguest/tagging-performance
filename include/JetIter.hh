#ifndef JET_ITER_HH
#define JET_ITER_HH

#include <cstddef>

class TreeBuffer; 

struct Jet { 
  Jet(); 
  Jet(const TreeBuffer&, int index); 
  float pt; 
  float eta; 
  float mv1; 
  float mv1c; 
  float mv2c00; 
  float mv2c10; 
  float mv2c20; 
  float mvb; 
  int truth_label; 
  float jf_pu; 
  float jf_pc; 
  float jf_pb; 
  float gaia_pu; 
  float gaia_pc; 
  float gaia_pb; 
  bool valid; 
}; 

class JetIter { 
public: 
  JetIter(TreeBuffer*); 
  class const_iterator { 
    friend class JetIter; 
  public: 
    const Jet& operator*() const; 
    const const_iterator& operator++(); 
    bool operator==(const const_iterator& other) const; 
    bool operator!=(const const_iterator& other) const; 
  private: 
    const_iterator(TreeBuffer*, int); 
    Jet m_jet; 
    size_t m_jet_n; 
    size_t m_jets_event; 
    int m_event_n; 
    int m_events; 
    TreeBuffer* m_buffer; 
  }; 
  const_iterator begin() const; 
  const_iterator end() const; 
private: 
  TreeBuffer* m_buffer; 
}; 

#endif
