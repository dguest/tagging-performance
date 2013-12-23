#include "JetIter.hh" 
#include "TreeBuffer.h"

Jet::Jet() : 
  pt(-999), 
  valid(false)
{ 
}

Jet::Jet(const TreeBuffer& buff, int index) : 
  pt(buff.jet_pt->at(index))
{ 
}

JetIter::JetIter(TreeBuffer& buff): 
  m_buffer(&buff)
{ 
}

JetIter::const_iterator JetIter::begin() const { 
  return const_iterator(m_buffer, 0); 
}
JetIter::const_iterator JetIter::end() const { 
  return const_iterator(m_buffer, m_buffer->size()); 
}

const Jet& JetIter::const_iterator::operator*() const { 
  return m_jet; 
}
const JetIter::const_iterator& JetIter::const_iterator::operator++() { 
  for (event_n = m_event_n + 1; event_n < m_events; event_n++) { 
    m_buffer->getEntry(event_n);     
    int n_jets_event = m_buffer->jet_pt->size(); 
    if (n_jets_event) { 
      m_jet = Jet(m_buffer, event_n); 
      m_event_n = event_n; 
      return *this; 
    }
  }
  m_jet = Jet(); 
  return *this; 
}

bool JetIter::const_iterator::operator==(
  const JetIter::const_iterator& other) const { 
  return m_event_n == other.m_event_n && m_jet_n == other.m_event_n; 
}
bool JetIter::const_iterator::operator!=(
  const JetIter::const_iterator& other) const { 
  return !(*this == other); 
}

JetIter::const_iterator::const_iterator(TreeBuffer* buff, int event) : 
  m_jet_n(0), 
  m_jets_event(buff->jet_pt->size()), 
  m_event_n(event), 
  m_events(buff->size()), 
  m_buffer(buff)
{ 
  if (event < m_events) { 
    m_jet = Jet(*m_buffer, event)
  }
}
