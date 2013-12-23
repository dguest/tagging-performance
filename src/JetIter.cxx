#include "JetIter.hh" 
#include "TreeBuffer.h"

#include <cassert> 

TagTriple::TagTriple() : pu(-999), pc(-999), pb(-999)
{ 
}

TagTriple::TagTriple(const TagVectors& buff, int index): 
  pu(buff.pu->at(index)), 
  pc(buff.pc->at(index)), 
  pb(buff.pb->at(index))
{ 
}

Jet::Jet() : 
  pt(-999), 
  valid(false)
{ 
}

Jet::Jet(const TreeBuffer& buff, int index) : 
  event(buff.entry()), 
  pt(buff.jet_pt->at(index)), 
  eta(buff.jet_pt->at(index)),
  valid(true), 
  mv1(buff.jet_MV1->at(index)), 
  mv1c(buff.jet_MV1c->at(index)), 
  mv2c00(buff.jet_MV2c00->at(index)), 
  mv2c10(buff.jet_MV2c10->at(index)), 
  mv2c20(buff.jet_MV2c20->at(index)), 
  mvb(buff.jet_MVb->at(index)), 
  truth_label(buff.jet_flavor_truth_label->at(index)), 
  gaia(buff.gaia, index), 
  jfit(buff.jfit, index), 
  jfc(buff.jfc, index)
{ 
}

JetIter::JetIter(TreeBuffer* buff):  
  m_buffer(buff)
{ 
}

JetIter::const_iterator JetIter::begin() const { 
  return const_iterator(m_buffer, 0); 
}
JetIter::const_iterator JetIter::end() const { 
  return const_iterator(m_buffer, m_buffer->size(), false); 
}

const Jet& JetIter::const_iterator::operator*() const { 
  return m_jet; 
}
const JetIter::const_iterator& JetIter::const_iterator::operator++() { 
  m_jet_n++; 
  if (m_jet_n < m_jets_event) { 
    assert(m_jet_n < m_buffer->jet_pt->size()); 
    m_jet = Jet(*m_buffer, m_jet_n); 
    return *this; 
  }
  for (int event_n = m_event_n + 1; event_n < m_events; event_n++) { 
    m_buffer->getEntry(event_n);     
    int n_jets_event = m_buffer->jet_pt->size(); 
    if (n_jets_event) { 
      m_jets_event = n_jets_event; 
      m_jet_n = 0; 
      m_jet = Jet(*m_buffer, m_jet_n); 
      m_event_n = event_n; 
      return *this; 
    }
  }
  m_jet = Jet(); 
  return *this; 
}

bool JetIter::const_iterator::operator==(
  const JetIter::const_iterator& other) const { 
  return m_event_n == other.m_event_n && m_jet_n == other.m_jet_n; 
}
bool JetIter::const_iterator::operator!=(
  const JetIter::const_iterator& other) const { 
  return !(*this == other); 
}

JetIter::const_iterator::const_iterator(TreeBuffer* buff, 
					int event, bool read) : 
  m_jet_n(0), 
  m_jets_event(0), 
  m_event_n(event), 
  m_events(buff->size()), 
  m_buffer(buff)
{ 
  if (event < m_events && read) { 
    m_buffer->getEntry(event); 
    m_jets_event = m_buffer->jet_pt->size(); 
    m_jet = Jet(*m_buffer, event); 
  }
}
