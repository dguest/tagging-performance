#ifndef JET_ITER_HH
#define JET_ITER_HH

class TreeBuffer; 

struct Jet { 
  Jet(const TreeBuffer&, int index); 
  float pt; 
}; 

class JetIter { 
public: 
  JetIter(TreeBuffer&); 
  class const_iterator { 
    friend class JetIter; 
  public: 
    const Jet& operator*() const; 
    const const_iterator& operator++(); 
    bool operator==(const const_iterator& other) const; 
    bool operator!=(const const_iterator& other) const; 
  private: 
    const_iterator(TreeBuffer*, int); 
    mutable Jet m_jet; 
    int m_jet_n; 
    int m_jets_event; 
    int m_event_n; 
    TreeBuffer* m_buffer; 
    mutable bool m_valid; 
  }; 
  const_iterator begin() const; 
  const_iterator end() const; 
private: 
  TreeBuffer* m_buffer; 
}; 

#endif
