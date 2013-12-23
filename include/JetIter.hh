#ifndef JET_ITER_HH
#define JET_ITER_HH

#include <cstddef>

class TreeBuffer; 
class TagVectors; 

struct TagTriple { 
  TagTriple(); 
  TagTriple(const TagVectors&, int index); 
  float pu; 
  float pc; 
  float pb; 
};

struct Jet { 
  Jet(); 
  Jet(const TreeBuffer&, int index); 
  int event; 
  float pt; 
  float eta; 
  bool valid; 
  float mv1; 
  float mv1c; 
  float mv2c00; 
  float mv2c10; 
  float mv2c20; 
  float mvb; 
  int truth_label; 
  TagTriple gaia; 
  TagTriple jfit; 
  TagTriple jfc; 
}; 

class JetIter { 
public: 
  JetIter(TreeBuffer*); 
  class const_iterator { 
    friend class JetIter; 
  public: 
    const_iterator() = delete; 
    const Jet& operator*() const; 
    const const_iterator& operator++(); 
    bool operator==(const const_iterator& other) const; 
    bool operator!=(const const_iterator& other) const; 
  private: 
    const_iterator(TreeBuffer*, int, bool read = true); 
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
